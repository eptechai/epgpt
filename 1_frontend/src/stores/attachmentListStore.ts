import { AttachmentStatus, type AttachmentItem } from '$lib/types';
import { writable } from 'svelte/store';
import type { AttachmentStatus as Attachment } from '../generated/client';

export interface AttachmentListState {
  attachmentMap: Map<string, AttachmentItem[]>;
}

const initialState: AttachmentListState = {
  attachmentMap: new Map()
};

const createAttachmentListStore = () => {
  const { subscribe, update } = writable<AttachmentListState>(initialState);

  const appendAttachmentItem = (conversationId: string, item: AttachmentItem) => {
    update((currentState) => {
      const updatedAttachmentMap = new Map(currentState.attachmentMap);
      const existingAttachments = updatedAttachmentMap.get(conversationId) || [];
      updatedAttachmentMap.set(conversationId, [...existingAttachments, item]);

      return {
        ...currentState,
        attachmentMap: updatedAttachmentMap
      };
    });
  };

  const setAttachmentItemList = (conversationId: string, items: AttachmentItem[]) => {
    update((currentState) => {
      const updatedAttachmentMap = new Map(currentState.attachmentMap);
      updatedAttachmentMap.set(conversationId, [...items]);

      return {
        ...currentState,
        attachmentMap: updatedAttachmentMap
      };
    });
  };

  const deleteAttachmentItem = (conversationId: string, attachmentId: string) => {
    update((currentState) => {
      const updatedAttachmentMap = new Map(currentState.attachmentMap);
      const currentAttachmentList = updatedAttachmentMap.get(conversationId) || [];

      const updatedAttachmentList = currentAttachmentList.filter((it) => {
        return it.attachment.id !== attachmentId;
      });

      updatedAttachmentMap.set(conversationId, updatedAttachmentList);
      return {
        ...currentState,
        attachmentMap: updatedAttachmentMap
      };
    });
  };

  const mapRemoteStatusToAttachmentStatus = (remoteStatus: string): AttachmentStatus => {
    switch (remoteStatus) {
      case 'PENDING':
        return AttachmentStatus.Pending;
      case 'UPLOADED':
        return AttachmentStatus.Uploaded;
      case 'INDEXED':
        return AttachmentStatus.Indexed;
      case 'ERRORED':
        return AttachmentStatus.Errored;
      default:
        throw new Error('Unknown status - ' + remoteStatus);
    }
  };

  const updateAttachmentItemStatus = (conversationId: string, attachment: Attachment) => {
    const status: AttachmentStatus = mapRemoteStatusToAttachmentStatus(attachment.status);

    update((currentState) => {
      const updatedAttachmentMap = new Map(currentState.attachmentMap);
      const existingAttachments = updatedAttachmentMap.get(conversationId) || [];

      const indexToUpdate = existingAttachments.findIndex((it) => {
        return it.attachment.id === attachment.id;
      });

      if (indexToUpdate !== -1) {
        const targetItem = existingAttachments[indexToUpdate];
        const updatedItem: AttachmentItem = {
          ...targetItem,
          status: status,
          attachment: {
            ...targetItem.attachment,
            status: attachment.status
          }
        };
        existingAttachments[indexToUpdate] = updatedItem;
        updatedAttachmentMap.set(conversationId, existingAttachments);
      }

      return { ...currentState, attachmentMap: updatedAttachmentMap };
    });
  };

  const updatePendingAttachmentItem = (
    conversationId: string,
    tempId: string,
    attachment: Attachment
  ) => {
    const status: AttachmentStatus = mapRemoteStatusToAttachmentStatus(attachment.status);

    update((currentState) => {
      const updatedAttachmentMap = new Map(currentState.attachmentMap);
      const existingAttachments = updatedAttachmentMap.get(conversationId) || [];

      const indexToUpdate = existingAttachments.findIndex((it) => {
        return it.attachment.id === tempId;
      });

      if (indexToUpdate !== -1) {
        const targetItem = existingAttachments[indexToUpdate];
        const updatedItem: AttachmentItem = {
          ...targetItem,
          status: status,
          attachment: {
            ...targetItem.attachment,
            id: attachment.id,
            status: attachment.status
          }
        };
        existingAttachments[indexToUpdate] = updatedItem;
        updatedAttachmentMap.set(conversationId, existingAttachments);
      }

      return { ...currentState, attachmentMap: updatedAttachmentMap };
    });
  };

  return {
    subscribe,
    appendAttachmentItem,
    setAttachmentItemList,
    deleteAttachmentItem,
    updatePendingAttachmentItem,
    updateAttachmentItemStatus
  };
};

export const attachmentListStore = createAttachmentListStore();
export type AttachmentListStore = ReturnType<typeof createAttachmentListStore>;
