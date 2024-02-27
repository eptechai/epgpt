import { get, writable } from 'svelte/store';
import type { Conversation } from '../generated/client';
import { makePagination, type Pagination } from '$lib/util/pagination';

export interface ConversationListState {
  conversationList: Pagination<Conversation[]>;
}

const initialState: ConversationListState = {
  conversationList: makePagination([])
};

const createConversationListStore = () => {
  const store = writable<ConversationListState>(initialState);
  const { subscribe, set, update } = store;

  const getConversationList = () => {
    return get(store).conversationList;
  };

  const appendConversation = (conversation: Conversation) => {
    update((currentState) => {
      const currentConversationList = currentState.conversationList;

      const conversationExists = currentConversationList.data.some(
        (existingConversation) => existingConversation.id === conversation.id
      );

      if (!conversationExists) {
        const updatedConversationList: Pagination<Conversation[]> = {
          ...currentConversationList,
          data: [conversation, ...currentConversationList.data]
        };
        return {
          ...currentState,
          conversationList: updatedConversationList
        };
      }
      return currentState;
    });
  };

  const updateConversation = (conversation: Conversation) => {
    update((currentState) => {
      const currentConversationList = currentState.conversationList;
      const indexToUpdate = currentConversationList.data.findIndex(
        (existingConversation) => existingConversation.id === conversation.id
      );

      if (indexToUpdate !== -1) {
        const itemToUpdate = currentConversationList.data[indexToUpdate];
        currentConversationList.data[indexToUpdate] = {
          ...itemToUpdate,
          ...conversation
        };
        const updatedConversationList: Pagination<Conversation[]> = {
          ...currentConversationList,
          data: currentConversationList.data
        };
        return {
          ...currentState,
          conversationList: updatedConversationList
        };
      }
      return currentState;
    });
  };

  const deleteConversation = (conversationId: string) => {
    update((currentState) => {
      const currentConversationList = currentState.conversationList;
      const updatedData = currentConversationList.data.filter((it) => {
        return it.id !== conversationId;
      });

      const updatedConversationList: Pagination<Conversation[]> = {
        ...currentConversationList,
        data: updatedData
      };

      return {
        ...currentState,
        conversationList: updatedConversationList
      };
    });
  };

  // Note: used in initial load of conversation list
  const setConversationList = (paginatedConversations: Pagination<Conversation[]>) => {
    const { data: newData, nextCursor } = paginatedConversations;
    set({ conversationList: { data: newData, nextCursor } });
  };

  // Note: used in infinite scroll of conversation list
  const appendConversationList = (paginatedConversations: Pagination<Conversation[]>) => {
    const { data: newData, nextCursor } = paginatedConversations;

    update((currentState) => {
      const currentConversationList = currentState.conversationList;
      const updatedConversationList: Pagination<Conversation[]> = {
        data: [...currentConversationList.data, ...newData],
        nextCursor
      };

      return {
        ...currentState,
        conversationList: updatedConversationList
      };
    });
  };

  return {
    subscribe,
    getConversationList,
    appendConversation,
    appendConversationList,
    deleteConversation,
    updateConversation,
    setConversationList
  };
};

export const conversationListStore = createConversationListStore();
export type ConversationListStore = ReturnType<typeof createConversationListStore>;
