import { PAGE_SIZE } from '$lib/constants';
import type {
  ConversationListResponse,
  ConversationResponse,
  ConversationService,
  ParamsResponse
} from '../../generated/client';
import { makeRequest } from './request';

export function makeConversationAPIClient(conversationService: ConversationService) {
  async function createConversation() {
    return conversationService.createConversationApiConversationPost();
  }

  async function getConversation(conversationId: string) {
    return conversationService.getConversationApiConversationIdGet(conversationId);
  }

  async function listConversations(nextCursor?: number, limit = PAGE_SIZE) {
    return conversationService.getConversationHistoryApiConversationListGet(limit, nextCursor);
  }

  async function deleteConversation(conversationId: string) {
    return conversationService.deleteConversationApiConversationIdDelete(conversationId);
  }

  async function getConversationParams(conversationId: string) {
    return conversationService.getParamsApiConversationIdParamsGet(conversationId);
  }

  async function updateConversationParams(conversationId: string, params: ParamsResponse) {
    return conversationService.configureParamsApiConversationIdParamsPost(conversationId, params);
  }

  async function serverGetConversation(
    serverFetch: (input: RequestInfo, init?: RequestInit) => Promise<Response>,
    conversationId: string
  ) {
    return makeRequest<ConversationResponse>(
      `/api/conversation/${conversationId}`,
      {
        method: 'GET'
      },
      serverFetch
    );
  }

  async function serverListConversations(
    serverFetch: (input: RequestInfo, init?: RequestInit) => Promise<Response>,
    nextCursor?: number,
    limit = PAGE_SIZE
  ) {
    return makeRequest<ConversationListResponse>(
      `/api/conversation/list`,
      {
        method: 'GET',
        queryParams: {
          limit,
          next_cursor: nextCursor
        }
      },
      serverFetch
    );
  }

  async function serverGetConversationParams(
    serverFetch: (input: RequestInfo, init?: RequestInit) => Promise<Response>,
    conversationId: string
  ) {
    return makeRequest<ParamsResponse>(
      `/api/conversation/${conversationId}/params`,
      {
        method: 'GET'
      },
      serverFetch
    );
  }

  return {
    createConversation,
    getConversation,
    listConversations,
    deleteConversation,
    getConversationParams,
    updateConversationParams,

    serverGetConversation,
    serverListConversations,
    serverGetConversationParams
  };
}

export type ConversationAPIClient = ReturnType<typeof makeConversationAPIClient>;
