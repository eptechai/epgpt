import { getContext, setContext } from 'svelte';
import { attachmentListStore, type AttachmentListStore } from '../stores/attachmentListStore';
import { conversationListStore, type ConversationListStore } from '../stores/conversationListStore';
import { conversationStore, type ConversationStore } from '../stores/conversationStore';
import { parametersStore, type ParametersStore } from '../stores/parametersStore';
import { userInfoStore, type UserInfoStore } from '../stores/userInfoStore';
import { makeAPIClient, type APIClient } from './apiClient';
import { notificationStore, type NotificationStore } from '../stores/notificationStore';
import { subSectorCompanyStore, type SubSectorCompanyStore } from '../stores/subSectorCompanyStore';
import { subQuestionListStore, type SubQuestionListStore } from '../stores/subQuestionListStore';

export const API_CONTEXT_KEY = 'apiClient';
export type APIContext = {
  apiClient: APIClient;
};

export const CONVERSATION_LIST_STORE_KEY = 'conversationListStore';
export type ConversationListStoreContext = {
  conversationListStore: ConversationListStore;
};

export const CONVERSATION_STORE_KEY = 'conversationStore';
export type ConversationStoreContext = {
  conversationStore: ConversationStore;
};

export const ATTACHMENT_LIST_STORE_KEY = 'attachmentListStore';
export type AttachmentListStoreContext = {
  attachmentListStore: AttachmentListStore;
};

export const PARAMETERS_STORE_KEY = 'parametersStore';
export type ParametersStoreContext = {
  parametersStore: ParametersStore;
};

export const USER_INFO_STORE_KEY = 'userInfoStore';
export type UserInfoStoreContext = {
  userInfoStore: UserInfoStore;
};

export const NOTIFICATION_STORE_KEY = 'notificationStore';
export type NotificationStoreContext = { notificationStore: NotificationStore };

export const SUBSECTOR_COMPANY_STORE_KEY = 'subSectorCompanyStore';
export type SubSectorCompanyStoreContext = { subSectorCompanyStore: SubSectorCompanyStore };

export const SUBQUESTION_LIST_STORE_KEY = 'subQuestionListStore';
export type SubQuestionStoreContext = { subQuestionListStore: SubQuestionListStore };

export enum ContextType {
  API_CLIENT = 'apiClient',
  CONVERSATION_LIST_STORE = 'conversationListStore',
  CONVERSATION_STORE = 'conversationStore',
  ATTACHMENT_LIST_STORE = 'attachmentListStore',
  PARAMETERS_STORE = 'parametersStore',
  USER_INFO_STORE = 'userInfoStore',
  NOTIFICATION_STORE = 'notificationStore',
  SUBSECTOR_COMPANY_STORE = 'subSectorCompanyStore',
  SUBQUESTION_LIST_STORE = 'subQuestionListStore'
}

export interface ContextValueMap {
  apiClient: APIClient;
  conversationListStore: ConversationListStore;
  conversationStore: ConversationStore;
  attachmentListStore: AttachmentListStore;
  parametersStore: ParametersStore;
  userInfoStore: UserInfoStore;
  notificationStore: NotificationStore;
  subSectorCompanyStore: SubSectorCompanyStore;
  subQuestionListStore: SubQuestionListStore;
}

export function useContexts(keys: ContextType[]) {
  const contextValueMap = keys.reduce((acc, it) => {
    switch (it) {
      case ContextType.API_CLIENT:
        acc[it] = getContext<APIContext>(it).apiClient;
        break;
      case ContextType.CONVERSATION_LIST_STORE:
        acc[it] = getContext<ConversationListStoreContext>(it).conversationListStore;
        break;
      case ContextType.CONVERSATION_STORE:
        acc[it] = getContext<ConversationStoreContext>(it).conversationStore;
        break;
      case ContextType.ATTACHMENT_LIST_STORE:
        acc[it] = getContext<AttachmentListStoreContext>(it).attachmentListStore;
        break;
      case ContextType.PARAMETERS_STORE:
        acc[it] = getContext<ParametersStoreContext>(it).parametersStore;
        break;
      case ContextType.USER_INFO_STORE:
        acc[it] = getContext<UserInfoStoreContext>(it).userInfoStore;
        break;
      case ContextType.NOTIFICATION_STORE:
        acc[it] = getContext<NotificationStoreContext>(it).notificationStore;
        break;
      case ContextType.SUBSECTOR_COMPANY_STORE:
        acc[it] = getContext<SubSectorCompanyStoreContext>(it).subSectorCompanyStore;
        break;
      case ContextType.SUBQUESTION_LIST_STORE:
        acc[it] = getContext<SubQuestionStoreContext>(it).subQuestionListStore;
        break;
      default:
        throw new Error(`Unknown context key: ${it}`);
    }
    return acc;
  }, {} as ContextValueMap);
  return contextValueMap;
}

export function setGlobalContexts() {
  setContext<APIContext>(API_CONTEXT_KEY, {
    apiClient: makeAPIClient()
  });
  setContext<ConversationListStoreContext>(CONVERSATION_LIST_STORE_KEY, {
    conversationListStore: conversationListStore
  });
  setContext<ConversationStoreContext>(CONVERSATION_STORE_KEY, {
    conversationStore: conversationStore
  });
  setContext<AttachmentListStoreContext>(ATTACHMENT_LIST_STORE_KEY, {
    attachmentListStore: attachmentListStore
  });
  setContext<ParametersStoreContext>(PARAMETERS_STORE_KEY, {
    parametersStore: parametersStore
  });
  setContext<UserInfoStoreContext>(USER_INFO_STORE_KEY, {
    userInfoStore: userInfoStore
  });
  setContext<NotificationStoreContext>(NOTIFICATION_STORE_KEY, {
    notificationStore: notificationStore
  });
  setContext<SubSectorCompanyStoreContext>(SUBSECTOR_COMPANY_STORE_KEY, {
    subSectorCompanyStore: subSectorCompanyStore
  });
  setContext<SubQuestionStoreContext>(SUBQUESTION_LIST_STORE_KEY, {
    subQuestionListStore: subQuestionListStore
  });
}
