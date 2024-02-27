import type {
  Conversation,
  ConversationListResponse,
  MessageListResponse,
  MessageResponse
} from '../../generated/client';

export type Pagination<T> = {
  data: T;
  nextCursor?: number;
};

export function makePagination<T>(data: T, nextCursor?: number): Pagination<T> {
  return {
    data,
    nextCursor
  };
}

export const makeConversationPagination = (
  genList: ConversationListResponse
): Pagination<Conversation[]> => {
  return makePagination(genList.conversations, genList.next_cursor);
};

export const makeMessagePagination = (
  genList: MessageListResponse
): Pagination<MessageResponse[]> => {
  return makePagination(genList.messages, genList.next_cursor);
};

export const PAGINATION_END_TIMESTAMP = 1;
