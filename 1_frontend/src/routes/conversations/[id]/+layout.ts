import makeAPIClient from '$lib/apiClient';
import {
  textRequestMessageItem,
  responseItem,
  uploadedAttachmentItem,
  indexedAttachmentItem,
  errorAttachmentItem,
  type AttachmentItem,
  type DialogueItem
} from '$lib/types.js';
import { makePagination, type Pagination } from '$lib/util/pagination.js';
import type { ParamsResponse } from '../../../generated/client/index.js';
import { conversationListStore } from '../../../stores/conversationListStore.js';
import { get } from 'svelte/store';
import { conversationStore } from '../../../stores/conversationStore.js';
import { attachmentListStore } from '../../../stores/attachmentListStore.js';
import { parametersStore } from '../../../stores/parametersStore.js';
import { notificationStore } from '../../../stores/notificationStore.js';

export async function load({ fetch: serverFetch, params }) {
  // Note: prefetch function does not have access to the context
  // so we need to access the `stores` directly
  // Note that we should only `read` from the stores, not `write` to them
  const apiClient = makeAPIClient();

  const conversationId = params.id;
  const respObj: {
    conversationId: string;
    remoteDialogueItems: Pagination<DialogueItem[]> | null;
    attachmentItems: AttachmentItem[];
    parametersResp: ParamsResponse | null;
  } = {
    conversationId,
    remoteDialogueItems: null,
    attachmentItems: [],
    parametersResp: null
  };

  const fetchDataPromises = [];

  // Note: Check if the conversation is already existed in the store
  const conversationList = get(conversationListStore).conversationList;
  if (
    conversationList.data.length === 0 ||
    !conversationList.data.some((it) => it.id === conversationId)
  ) {
    try {
      await apiClient.serverGetConversation(serverFetch, params.id);
    } catch (e: any) {
      console.log('Failed to fetch conversation', e);
      return;
    }
  }

  // Note: Check if the message list is already existed in the store
  const dialogueMap = get(conversationStore).dialogueMap;
  const dialogueItems = dialogueMap.get(conversationId);
  if (dialogueItems == null) {
    fetchDataPromises.push(
      apiClient.serverListMessages(serverFetch, params.id).then((messageListResp) => {
        const remoteDialogueItems: DialogueItem[] = messageListResp.messages.map((it) => {
          if (it.author === 'USER') {
            return textRequestMessageItem(it.id, it.text);
          }
          return responseItem({
            id: it.id,
            response: it.text,
            citations: it.citations,
            isFeedbackPositive: it.isFeedbackPositive
          });
        });
        respObj.remoteDialogueItems = makePagination<DialogueItem[]>(
          remoteDialogueItems,
          messageListResp.next_cursor
        );
      })
    );
  } else {
    respObj.remoteDialogueItems = dialogueItems;
  }

  const attachmentMap = get(attachmentListStore).attachmentMap;
  const attachmentItems = attachmentMap.get(conversationId);
  if (attachmentItems == null) {
    fetchDataPromises.push(
      apiClient.serverListAttachments(serverFetch, params.id).then((attachmentListResp) => {
        const attachmentItems = attachmentListResp.attachments.map((it) => {
          if (it.status === 'UPLOADED') {
            return uploadedAttachmentItem(it);
          } else if (it.status === 'INDEXED') {
            return indexedAttachmentItem(it);
          }
          return errorAttachmentItem(it);
        });
        respObj.attachmentItems = attachmentItems;
      })
    );
  } else {
    respObj.attachmentItems = attachmentItems;
  }

  const parametersMap = get(parametersStore).parametersMap;
  const parametersResp = parametersMap.get(conversationId) ?? null;
  if (parametersResp == null) {
    fetchDataPromises.push(
      apiClient.serverGetConversationParams(serverFetch, params.id).then((parametersResp) => {
        respObj.parametersResp = parametersResp;
      })
    );
  } else {
    respObj.parametersResp = parametersResp;
  }

  try {
    await Promise.all(fetchDataPromises);
  } catch (e: any) {
    notificationStore.handleError(e, `Failed to prefetch data: ${e.message}`);
  }
  return respObj;
}
