import {
  ResponseItemType,
  type DialogueItem,
  MessageItemType,
  type ResponseItem
} from '$lib/types';
import { throttle } from '$lib/util/throttle';
import { get, writable } from 'svelte/store';
import type { CitationResponse } from '../generated/client';
import { makePagination, type Pagination } from '$lib/util/pagination';

export const MESSAGE_ID_PLACEHOLDER = 'MESSAGE_ID_PLACEHOLDER';
export interface ConversationState {
  dialogueMap: Map<string, Pagination<DialogueItem[]>>;
}

const initialState: ConversationState = {
  dialogueMap: new Map()
};

const createConversationStore = () => {
  const store = writable<ConversationState>(initialState);
  const { subscribe, update } = store;

  const getDialogueItemList = (conversationId: string) => {
    return get(store).dialogueMap.get(conversationId) ?? makePagination<DialogueItem[]>([]);
  };

  // Note: used in initial load of dialogue list
  const setDialogueItemList = (
    conversationId: string,
    paginatedItems: Pagination<DialogueItem[]>
  ) => {
    update((currentState) => {
      const updatedDialogueMap = new Map(currentState.dialogueMap);
      updatedDialogueMap.set(conversationId, paginatedItems);

      return {
        ...currentState,
        dialogueMap: updatedDialogueMap
      };
    });
  };

  // Note: used in infinite scroll of dialogue list
  const prependDialogueItemList = (
    conversationId: string,
    paginatedItems: Pagination<DialogueItem[]>
  ) => {
    const { data: newData, nextCursor } = paginatedItems;

    update((currentState) => {
      const updatedDialogueMap = new Map(currentState.dialogueMap);
      const currentDialogueList =
        updatedDialogueMap.get(conversationId) ?? makePagination<DialogueItem[]>([]);
      const updatedDialogueList: Pagination<DialogueItem[]> = {
        data: [...newData, ...currentDialogueList.data],
        nextCursor
      };
      updatedDialogueMap.set(conversationId, updatedDialogueList);
      return {
        ...currentState,
        dialogueMap: updatedDialogueMap
      };
    });
  };

  const appendDialogueItem = (conversationId: string, item: DialogueItem) => {
    update((currentState) => {
      const updatedDialogueMap = new Map(currentState.dialogueMap);
      const currentDialogueList =
        updatedDialogueMap.get(conversationId) ?? makePagination<DialogueItem[]>([]);
      const updatedDialogueList: Pagination<DialogueItem[]> = {
        data: [...currentDialogueList.data, item],
        nextCursor: currentDialogueList.nextCursor
      };
      updatedDialogueMap.set(conversationId, updatedDialogueList);
      return {
        ...currentState,
        dialogueMap: updatedDialogueMap
      };
    });
  };

  const removeLoadingItem = (conversationId: string) => {
    update((currentState) => {
      const updatedDialogueMap = new Map(currentState.dialogueMap);
      const currentDialogueList =
        updatedDialogueMap.get(conversationId) ?? makePagination<DialogueItem[]>([]);
      const updatedDialogueList: Pagination<DialogueItem[]> = {
        data: currentDialogueList.data.filter((item) => item.type !== ResponseItemType.Loading),
        nextCursor: currentDialogueList.nextCursor
      };
      updatedDialogueMap.set(conversationId, updatedDialogueList);
      return {
        ...currentState,
        dialogueMap: updatedDialogueMap
      };
    });
  };

  const updateLatestResponseItemResponse = throttle(
    ({
      conversationId,
      response
    }: {
      conversationId: string;
      messageId: string;
      response: string;
    }) => {
      update((currentState) => {
        const updatedDialogueMap = new Map(currentState.dialogueMap);
        const currentDialogueList =
          updatedDialogueMap.get(conversationId) ?? makePagination<DialogueItem[]>([]);
        const lastItem = currentDialogueList.data[
          currentDialogueList.data.length - 1
        ] as ResponseItem;

        if (lastItem) {
          const updatedItem: ResponseItem = {
            ...lastItem,
            response: {
              ...lastItem.response,
              response: response
            }
          };
          currentDialogueList.data[currentDialogueList.data.length - 1] = updatedItem;
          const updatedDialogueList: Pagination<DialogueItem[]> = {
            data: currentDialogueList.data,
            nextCursor: currentDialogueList.nextCursor
          };
          updatedDialogueMap.set(conversationId, updatedDialogueList);
        }
        return lastItem ? { ...currentState, dialogueMap: updatedDialogueMap } : currentState;
      });
    },
    500
  );

  const updateLatestResponseItemCitations = (
    conversationId: string,
    citations: CitationResponse[]
  ) => {
    update((currentState) => {
      const updatedDialogueMap = new Map(currentState.dialogueMap);
      const currentDialogueList =
        updatedDialogueMap.get(conversationId) ?? makePagination<DialogueItem[]>([]);
      const lastItem = currentDialogueList.data[
        currentDialogueList.data.length - 1
      ] as ResponseItem;

      if (lastItem) {
        const updatedItem: ResponseItem = {
          ...lastItem,
          response: {
            ...lastItem.response,
            citations: [...citations]
          }
        };
        currentDialogueList.data[currentDialogueList.data.length - 1] = updatedItem;
        const updatedDialogueList: Pagination<DialogueItem[]> = {
          data: currentDialogueList.data,
          nextCursor: currentDialogueList.nextCursor
        };
        updatedDialogueMap.set(conversationId, updatedDialogueList);
      }
      return lastItem ? { ...currentState, dialogueMap: updatedDialogueMap } : currentState;
    });
  };

  const updateMessagePlaceholderId = (conversationId: string, messageId: string) => {
    update((currentState) => {
      const updatedDialogueMap = new Map(currentState.dialogueMap);
      const currentDialogueList =
        updatedDialogueMap.get(conversationId) ?? makePagination<DialogueItem[]>([]);

      if (currentDialogueList.data.length > 0) {
        const indexToUpdate = currentDialogueList.data.findIndex((it) => {
          return (
            it.type === MessageItemType.TextRequestMessage &&
            it.messageId === MESSAGE_ID_PLACEHOLDER
          );
        });

        if (indexToUpdate !== -1) {
          const itemToUpdate = currentDialogueList.data[indexToUpdate];
          currentDialogueList.data[indexToUpdate] = {
            ...itemToUpdate,
            messageId
          } as DialogueItem;

          const updatedDialogueList: Pagination<DialogueItem[]> = {
            data: currentDialogueList.data,
            nextCursor: currentDialogueList.nextCursor
          };
          updatedDialogueMap.set(conversationId, updatedDialogueList);
          return {
            ...currentState,
            dialogueMap: updatedDialogueMap
          };
        }
      }
      return currentState;
    });
  };

  return {
    subscribe,
    getDialogueItemList,
    setDialogueItemList,
    prependDialogueItemList,
    appendDialogueItem,
    removeLoadingItem,
    updateResponseItemResponse: (conversationId: string, messageId: string, response: string) => {
      updateLatestResponseItemResponse({ conversationId, messageId, response });
    },
    updateLatestResponseItemCitations,
    updateMessagePlaceholderId
  };
};

export const conversationStore = createConversationStore();
export type ConversationStore = ReturnType<typeof createConversationStore>;
