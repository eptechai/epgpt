<script lang="ts">
  import { Drawer, CloseButton, type drawerTransitionParamTypes } from 'flowbite-svelte';
  import { sineIn } from 'svelte/easing';
  import Dropzone from 'svelte-file-dropzone/Dropzone.svelte';
  import { ImgType, getImgPath } from '$lib/util/images';
  import Modal from '../Modal.svelte';
  import PendingUploadModalView from './PendingUploadModalView.svelte';
  import type { AttachmentListState } from '../../../stores/attachmentListStore';
  import {
    pendingAttachmentItem,
    type AttachmentItem,
    AttachmentStatus,
    isAttachmentProccesed
  } from '$lib/types';
  import { onDestroy, onMount } from 'svelte';
  import { useContexts, ContextType } from '$lib/context';
  import AttachmentCell from './AttachmentCell.svelte';
  import type { AttachmentStatus as Attachment } from '../../../generated/client';
  import AttachmentDeletionModalView from './AttachmentDeletionModalView.svelte';
  import SelectCompanyModalView from '../SelectCompany/SelectCompanyModalView.svelte';
  import type { FileCompanyUpdate, FileTableData } from './types';

  export let conversationId: string;
  export let isDrawerHidden: boolean;
  export let onRequestClose: () => void;

  const { apiClient, attachmentListStore, notificationStore } = useContexts([
    ContextType.API_CLIENT,
    ContextType.ATTACHMENT_LIST_STORE,
    ContextType.NOTIFICATION_STORE
  ]);

  let fileInput: HTMLInputElement;
  let transitionParamsRight: drawerTransitionParamTypes = {
    x: 450,
    duration: 200,
    easing: sineIn
  };
  let selectedFileName: string;
  let fileSizeError = false;
  let attachmentListState: AttachmentListState;
  const unsubscribe = attachmentListStore.subscribe((value) => {
    attachmentListState = value;
  });
  let attachmentList: AttachmentItem[];
  $: {
    attachmentList = attachmentListState.attachmentMap.get(conversationId) ?? [];
  }

  let maxFileSizeAllowed = 10 * 1024 * 1024; // 10MB

  let pendingUploadFiles: File[] = [];
  function handleFilesSelect(e: CustomEvent<any>) {
    const { acceptedFiles } = e.detail;
    // Note: Filter out duplicate file names and files greater than 10mb
    const uniqueAcceptedFiles = (acceptedFiles as File[]).filter((file) => {
      return !pendingUploadFiles.some((existingFile) => existingFile.name === file.name);
    });

    const validFiles = uniqueAcceptedFiles.filter((file) => file.size <= maxFileSizeAllowed);

    pendingUploadFiles = [...pendingUploadFiles, ...validFiles];
    if (pendingUploadFiles.length === 0) {
      notificationStore.handleWarning('File size should be less than 10MB');
    } else if (validFiles.length !== uniqueAcceptedFiles.length) {
      fileSizeError = true;
    }

    openModal();
  }

  const handleUploadFiles = async (files: FileTableData[]) => {
    pendingUploadFiles = pendingUploadFiles.filter(
      (file) => !files.map((it) => it.file.name).includes(file.name)
    );

    files.forEach((file) => {
      const existedAttachmentIdx = attachmentList.findIndex(
        (it) => it.attachment.name === file.file.name
      );
      const tempId = `pending-id-${Date.now().toString()}`;
      if (existedAttachmentIdx !== -1) {
        attachmentListStore.updateAttachmentItemStatus(conversationId, {
          ...attachmentList[existedAttachmentIdx].attachment,
          status: AttachmentStatus.Pending
        });
      } else {
        attachmentListStore.appendAttachmentItem(
          conversationId,
          pendingAttachmentItem({
            id: tempId,
            name: file.file.name,
            status: AttachmentStatus.Pending
          })
        );
      }
      uploadFile(file, tempId).then((remoteAttachment) => {
        if (remoteAttachment && !isAttachmentProccesed(remoteAttachment)) {
          startPollingAttachmentStatus(conversationId, remoteAttachment.id);
        }
      });
    });
  };

  const uploadFile = async (fileData: FileTableData, tempId: string) => {
    try {
      if (fileData.company == null || fileData.year == null) {
        throw new Error('Unexpected company/year is null');
      }
      const remoteAttachment = await apiClient.uploadAttachment(conversationId, {
        attachment: fileData.file,
        company: fileData.company,
        year: fileData.year.toString()
      });
      processAttachmentStatus(remoteAttachment, tempId);
      return remoteAttachment;
    } catch (e: any) {
      notificationStore.handleError(
        e,
        `Failed to upload file - ${fileData.file.name}: ${e.message}`
      );
    }
  };

  const startPollingAttachmentStatus = (conversationId: string, attachmentId: string) => {
    const pollInterval = 5000;
    let timeoutId: NodeJS.Timeout;

    const poll = async () => {
      try {
        const remoteAttachment = await apiClient.getAttachmentStatus(conversationId, attachmentId);
        processAttachmentStatus(remoteAttachment);
        if (isAttachmentProccesed(remoteAttachment)) {
          clearTimeout(timeoutId);
          return;
        }
        // Note: Keep Polling if the attachment is not processed
        timeoutId = setTimeout(poll, pollInterval);
      } catch (e: any) {
        clearTimeout(timeoutId);
        notificationStore.handleError(e, `Error polling attachment status: ${e.message}`);
      }
    };
    timeoutId = setTimeout(poll, pollInterval);
  };

  function checkTempAttachmentId(tempId: string): boolean {
    return attachmentList.some((it) => it.attachment.id === tempId);
  }

  function processAttachmentStatus(attachment: Attachment, tempId?: string) {
    if (tempId && checkTempAttachmentId(tempId)) {
      attachmentListStore.updatePendingAttachmentItem(conversationId, tempId, attachment);
    } else {
      attachmentListStore.updateAttachmentItemStatus(conversationId, attachment);
    }
  }

  let showModal = false;
  const openModal = () => {
    if (pendingUploadFiles.length === 0) {
      return;
    }
    showModal = true;
  };
  const closeModal = () => {
    showModal = false;
    fileSizeError = false;
  };

  let showDeletionModal = false;
  const triggerDeletion = (attachment: Attachment) => {
    pendingDeleteAttachment = attachment;
    showDeletionModal = true;
  };
  const closeDeletionModal = () => {
    showDeletionModal = false;
  };

  // Attachement Deletion
  let hoveredAttachment: Attachment | undefined;
  let pendingDeleteAttachment: Attachment | undefined;
  const handleHoverAttachmentItem = (attachment?: Attachment) => {
    if (attachment && !isAttachmentProccesed(attachment)) {
      return;
    }
    hoveredAttachment = attachment;
  };

  const handleDeleteAttachment = async (_pendingDeleteAttachment: Attachment) => {
    try {
      attachmentListStore.deleteAttachmentItem(conversationId, _pendingDeleteAttachment.id);
      await apiClient.deleteAttachment(conversationId, _pendingDeleteAttachment.id);
    } catch (e: any) {
      notificationStore.handleError(e, `Failed to delete conversation: ${e.message}`);
    }
  };

  onMount(() => {
    attachmentList.forEach((it) => {
      if (!isAttachmentProccesed(it.attachment)) {
        startPollingAttachmentStatus(conversationId, it.attachment.id);
      }
    });
  });

  onDestroy(() => {
    unsubscribe();
  });

  let showSelectCompanyModal = false;
  const closeSelectCompanyModal = () => {
    showSelectCompanyModal = false;
  };

  const onSelectCompanyRequest = (filename: string) => {
    showSelectCompanyModal = true;
    selectedFileName = filename;
  };

  let fileUpdate: FileCompanyUpdate;
  const updatePendingFile = (newInfo: FileCompanyUpdate) => {
    fileUpdate = newInfo;
  };
</script>

<div>
  <Drawer
    activateClickOutside={false}
    placement="right"
    transitionType="fly"
    transitionParams={transitionParamsRight}
    bind:hidden={isDrawerHidden}
    divClass={'flex flex-col overflow-y-auto z-50 p-4 bg-white shadow-[rgba(0,_0,_0,_0.24)_0px_3px_8px] dark:bg-gray-800 max-w-max'}
    width={'w-[450px]'}
    bgColor={'bg-white'}
    bgOpacity={'bg-opacity-80'}
  >
    <div class="flex items-center mb-4">
      <div class="title">Attachments <br /><span class="title-id">({conversationId})</span></div>
      <CloseButton on:click={onRequestClose} class="mb-4 dark:text-white" />
    </div>
    <p class="mb-2 text-sm text-gray-500">
      The uploaded attachments will be a part of the sources for citations once the statuses are
      marked as Processed.
    </p>
    <button
      class="preview-pending-upload-button"
      on:click={openModal}
      disabled={pendingUploadFiles.length === 0}
    >
      Preview Pending Upload Files
    </button>
    <div class="uploaded-attachments-container">
      {#each attachmentList as item}
        <!-- svelte-ignore a11y-no-static-element-interactions -->
        <div
          class={'attachment-cell-wrapper'}
          on:mouseenter={() => {
            handleHoverAttachmentItem(item.attachment);
          }}
          on:mouseleave={() => {
            handleHoverAttachmentItem();
          }}
        >
          <AttachmentCell {conversationId} {item} />
          {#if hoveredAttachment && hoveredAttachment.id === item.attachment.id}
            <div class="attachment-cell-action-view">
              <div class={'attachment-cell-gradiant-view'} />
              <button
                class={'attachment-cell-icon-button'}
                on:click={() => {
                  triggerDeletion(item.attachment);
                }}
              >
                <img
                  class="attachment-cell-delete-icon"
                  src={getImgPath(ImgType.IconDeleteDark)}
                  alt="delete"
                  width={20}
                />
              </button>
            </div>
          {/if}
        </div>
      {/each}
    </div>
    <Dropzone
      disableDefaultStyles={true}
      containerClasses={'custom-dropzone'}
      inputElement={fileInput}
      accept={'.pdf'}
      on:drop={handleFilesSelect}
    >
      <div class="dropzone-display">
        <div class="icon-wrapper">
          <div class="icon">
            <img src={getImgPath(ImgType.IconAddWhite)} alt="New Attachment" width="20" />
          </div>
        </div>
        <div class="dropzone-title">Upload New Attachments</div>
        <div class="dropzone-sutitle">Drag and Drop</div>
      </div>
    </Dropzone>
  </Drawer>
  <Modal bind:showModal>
    <PendingUploadModalView
      {pendingUploadFiles}
      onRequestClose={closeModal}
      onUploadFiles={handleUploadFiles}
      showMaxFilesizeError={fileSizeError}
      {onSelectCompanyRequest}
      {fileUpdate}
    />
  </Modal>
  {#if pendingDeleteAttachment}
    <Modal bind:showModal={showDeletionModal}>
      <AttachmentDeletionModalView
        attachment={pendingDeleteAttachment}
        onRequestClose={closeDeletionModal}
        onDelete={handleDeleteAttachment}
      />
    </Modal>
  {/if}

  <Modal bind:showModal={showSelectCompanyModal}>
    <SelectCompanyModalView
      onClose={closeSelectCompanyModal}
      filename={selectedFileName}
      onCompanySelect={updatePendingFile}
    />
  </Modal>
</div>

<style lang="scss">
  @import '../../../global.scss';

  .title {
    font-size: 18px;
    font-weight: 600;
    color: $theme-charcoal;
  }

  .title-id {
    font-size: 16px;
    color: $theme-stale-grey;
  }

  .uploaded-attachments-container {
    display: flex;
    flex-direction: column;
    margin-bottom: 12px;
    height: calc(100vh - 485px);
    overflow-y: scroll;

    @include custom-scroll-bar();
  }

  :global(.custom-dropzone) {
    display: flex;
    flex-direction: column;
    padding: 12px;
    height: 260px;
    margin-top: auto;

    background-image: url("data:image/svg+xml,%3csvg width='100%25' height='100%25' xmlns='http://www.w3.org/2000/svg'%3e%3crect width='100%25' height='100%25' fill='none' rx='20' ry='20' stroke='%23AEB8C2FF' stroke-width='6' stroke-dasharray='6%2c 14' stroke-dashoffset='0' stroke-linecap='square'/%3e%3c/svg%3e");
    border-radius: 20px;
  }

  .dropzone-display {
    display: flex;
    height: 100%;
    flex-direction: column;
    justify-content: center;
    align-items: center;
  }

  .icon-wrapper {
    width: 50px;
    display: flex;
    flex-direction: column;
    margin-bottom: 12px;
  }

  .icon {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 50px;
    height: 50px;
    border-radius: 50%;
    background-color: $theme-blue;
    font-weight: bold;
  }

  .dropzone-title {
    font-size: 16px;
    font-weight: 600;
    color: $theme-charcoal;
  }

  .dropzone-sutitle {
    font-size: 14px;
    font-weight: 400;
    color: $theme-charcoal;
  }

  .preview-pending-upload-button {
    display: flex;
    align-self: flex-start;

    color: $theme-blue;
    border-radius: 8px;
    padding: 10px 0;
    margin-bottom: 16px;
    font-size: 16px;
    font-weight: 600;

    &:disabled {
      color: #999999;
      cursor: not-allowed;
    }

    &:hover:not(:disabled) {
      color: darken($theme-blue, 20%);
      cursor: pointer;
    }
  }

  .attachment-cell-wrapper {
    position: relative;
    height: auto;
  }

  .attachment-cell-action-view {
    position: absolute;
    top: 0;
    right: 0;
    bottom: 0;

    display: flex;
    flex-direction: row;
    justify-content: flex-end;
    align-items: center;
    width: 80px;
    pointer-events: none;

    border-top-right-radius: 8px;
    border-bottom-right-radius: 8px;
  }

  .attachment-cell-gradiant-view {
    flex: 3;
    background: linear-gradient(to right, transparent 5%, white);
    height: 100%;
    pointer-events: none;
  }

  .attachment-cell-icon-button {
    flex: 2;
    height: 100%;

    display: flex;
    flex-direction: row;
    justify-content: center;
    align-items: center;
    background-color: white;
    border-top-right-radius: 8px;
    border-bottom-right-radius: 8px;
    padding-right: 4px;
    pointer-events: all;
  }

  .attachment-cell-delete-icon {
    padding-bottom: 6px;
    &:hover:not(:disabled) {
      transform: scale(1.1);
    }
  }
</style>
