import makeAPIClient from '$lib/apiClient';
import { USER_INFO_LOCAL_STORAGE_KEY } from '$lib/constants.js';
import { makeConversationPagination, type Pagination } from '$lib/util/pagination.js';
import { getLocalStorageItem } from '$lib/util/localStorage.js';
import type { UserInfo } from '$lib/model/user.js';
import type { Conversation, SubsectorResponse } from '../generated/client/index.js';
import { conversationListStore } from '../stores/conversationListStore.js';
import { get } from 'svelte/store';
import { notificationStore } from '../stores/notificationStore.js';

export async function load({ fetch: serverFetch }) {
  // Note: prefetch function does not have access to the context
  // so we need to access the `stores` directly
  // Note that we should only `read` from the stores, not `write` to them
  const apiClient = makeAPIClient();

  const respObj: {
    userInfo: UserInfo | null;
    paginatedConversations: Pagination<Conversation[]> | null;
    subSectorCompanies: Array<SubsectorResponse> | null;
  } = {
    userInfo: null,
    paginatedConversations: null,
    subSectorCompanies: null
  };

  const fetchDataPromises = [];
  const conversationList = get(conversationListStore).conversationList;
  // Note: if there is only one conversation (the one just created), we need to fetch the conversation list
  if (conversationList.data.length <= 1) {
    fetchDataPromises.push(
      apiClient.serverListConversations(serverFetch).then((conversationListResp) => {
        respObj.paginatedConversations = makeConversationPagination(conversationListResp);
      })
    );
  } else {
    respObj.paginatedConversations = conversationList;
  }

  const userInfo = getLocalStorageItem(USER_INFO_LOCAL_STORAGE_KEY);
  if (userInfo == null) {
    fetchDataPromises.push(
      apiClient.serverGetUserInfo(serverFetch).then((resp) => {
        respObj.userInfo = resp as UserInfo;
      })
    );
  }

  fetchDataPromises.push(
    apiClient.serverGetSubSectorsAndCompanies(serverFetch).then((resp) => {
      respObj.subSectorCompanies = resp.subsectors;
    })
  );

  try {
    await Promise.all(fetchDataPromises);
  } catch (e: any) {
    notificationStore.handleError(e, `Failed to prefetch data: ${e.message}`);
  }
  return respObj;
}
