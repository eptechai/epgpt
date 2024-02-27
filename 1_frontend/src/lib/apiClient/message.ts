import { PAGE_SIZE } from '$lib/constants';
import type { MessageRequestPayload } from '$lib/model/request';
import type { MessageFeedback, MessageListResponse, MessageService } from '../../generated/client';
import { makeRequest, makeStreamRequest, type RequestData } from './request';

export function makeMessageAPIClient(messageService: MessageService) {
  // HTTP2 Streaming
  async function createMessage(conversationId: string, payload: MessageRequestPayload) {
    return messageService.postMessageApiConversationIdMessagePost(conversationId, {
      prompt: payload.message
    });
  }

  async function cancelMessageResponse(conversationId: string, messageId: string) {
    return messageService.cancelStreamingApiConversationIdMessageMessageIdCancelPost(
      conversationId,
      messageId
    );
  }

  async function listMessages(conversationId: string, nextCursor?: number, limit = PAGE_SIZE) {
    return messageService.getMessagesApiConversationIdMessageListGet(
      conversationId,
      limit,
      nextCursor
    );
  }

  async function getMessageCitations(conversationId: string, messageId: string) {
    return messageService.getCitationsApiConversationIdMessageMessageIdCitationsGet(
      conversationId,
      messageId
    );
  }

  async function rateResponse(
    conversationId: string,
    messageId: string,
    requestBody: MessageFeedback
  ) {
    return messageService.saveUserFeedbackApiConversationIdMessageMessageIdFeedbackPost(
      conversationId,
      messageId,
      requestBody
    );
  }

  async function getSubQuestions(conversationId: string, messageId: string) {
    return messageService.getSubquestionsApiConversationIdMessageMessageIdSubQuestionListGet(
      conversationId,
      messageId
    );
  }

  async function streamMessageCreation(conversationId: string, prompt: string) {
    const requestData: RequestData = {
      method: 'POST',
      payload: {
        prompt
      }
    };

    return makeStreamRequest(`/api/conversation/${conversationId}/message`, requestData);
  }

  async function serverListMessages(
    serverFetch: (input: RequestInfo, init?: RequestInit) => Promise<Response>,
    conversationId: string,
    nextCursor?: number,
    limit = PAGE_SIZE
  ) {
    return makeRequest<MessageListResponse>(
      `/api/conversation/${conversationId}/message/list`,
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

  return {
    createMessage,
    cancelMessageResponse,
    listMessages,
    getMessageCitations,
    streamMessageCreation,
    rateResponse,
    getSubQuestions,
    serverListMessages
  };
}

export type MessageAPIClient = ReturnType<typeof makeMessageAPIClient>;
