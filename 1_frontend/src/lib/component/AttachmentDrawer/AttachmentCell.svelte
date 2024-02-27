<script lang="ts">
  import { ImgType, getImgPath } from '$lib/util/images';
  import { Spinner } from 'flowbite-svelte';
  import { AttachmentStatus, type AttachmentItem } from '$lib/types';
  import { useContexts, ContextType } from '$lib/context';
  import classNames from 'classnames';

  export let conversationId: string;
  export let item: AttachmentItem;
  $: isDownloadable = item.status === AttachmentStatus.Indexed;

  const { apiClient, notificationStore } = useContexts([
    ContextType.API_CLIENT,
    ContextType.ATTACHMENT_LIST_STORE,
    ContextType.NOTIFICATION_STORE
  ]);

  const handleDownload = async () => {
    if (!isDownloadable) {
      return;
    }
    try {
      const blob = await apiClient.downloadAttachment(conversationId, item.attachment.id);
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = item.attachment.name;

      // Simulate a click event on the link
      link.click();

      // Clean up by revoking the object URL
      URL.revokeObjectURL(url);
    } catch (e: any) {
      notificationStore.handleError(e, `Failed to download the file - ${e.message}`);
    }
  };
</script>

<!-- svelte-ignore a11y-click-events-have-key-events -->
<!-- svelte-ignore a11y-no-static-element-interactions -->
<div
  class={classNames('item-container', isDownloadable ? 'hoverable' : '')}
  on:click={handleDownload}
>
  <div class="item-status">
    {#if item.status === AttachmentStatus.Pending}
      <img src={getImgPath(ImgType.IconPending)} alt="pending" width={30} />
    {:else if item.status === AttachmentStatus.Uploaded}
      <Spinner size={'8'} />
    {:else if item.status === AttachmentStatus.Indexed}
      <img src={getImgPath(ImgType.IconSuccess)} alt="processed" width={30} />
    {:else if item.status === AttachmentStatus.Errored}
      <img src={getImgPath(ImgType.IconFailure)} alt="error" width={32} />
    {/if}
  </div>
  <div class="item-filename">{item.attachment.name}</div>
</div>

<style lang="scss">
  @import '../../../global.scss';

  .item-container {
    min-height: 48px;
    display: flex;
    flex-direction: row;
    align-items: center;
    margin-bottom: 4px;
    padding: 8px;
    border-radius: 8px;
    cursor: default;

    &.hoverable {
      &:hover {
        cursor: pointer;
        background-color: #f2f2f2;
      }
    }
  }

  .item-status {
    display: flex;
    align-items: center;
    justify-content: center;
    flex: 1;
  }

  .item-filename {
    display: flex;
    align-items: center;
    font-size: 14px;
    margin-left: 8px;
    flex: 10;
  }
</style>
