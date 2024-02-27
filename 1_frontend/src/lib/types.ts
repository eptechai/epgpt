import type { AttachmentStatus as Attachment, MessageListResponse } from '../generated/client';
import type { Response } from './model/response';
import { makePagination, type Pagination } from './util/pagination';

// --- ResponseItem ---
export type ResponseItemBase = {
  responseId: string;
};

export enum ResponseItemType {
  Loading = 'Loading',
  Response = 'Response',
  Failure = 'Failure'
}

export type LoadingItem = {
  type: ResponseItemType.Loading;
};
export const loadingItem = (): LoadingItem => {
  return {
    type: ResponseItemType.Loading
  };
};

export type ResponseItem = {
  type: ResponseItemType.Response;
  response: Response;
};
export const responseItem = (response: Response): ResponseItem => {
  return {
    type: ResponseItemType.Response,
    response
  };
};

export type FailureItem = ResponseItemBase & {
  type: ResponseItemType.Failure;
  errorMessage: string;
};
export const failureResponseItem = (responseId: string, errorMessage: string): FailureItem => {
  return {
    type: ResponseItemType.Failure,
    responseId,
    errorMessage
  };
};

// --- MessageItem ---
export type MessageItemBase = {
  messageId: string;
};

export enum MessageItemType {
  TextRequestMessage = 'TextRequestMessage'
}

export type TextRequestMessageItem = MessageItemBase & {
  type: MessageItemType.TextRequestMessage;
  data: string;
};
export const textRequestMessageItem = (messageId: string, data: string): TextRequestMessageItem => {
  return {
    type: MessageItemType.TextRequestMessage,
    messageId,
    data
  };
};

export type MessageItem = TextRequestMessageItem;
export type DialogueItem = MessageItem | LoadingItem | ResponseItem | FailureItem;

export const convertMessageListResponseToPaginatedDialogueItems = (
  resp: MessageListResponse
): Pagination<DialogueItem[]> => {
  const remoteDialogueItems: DialogueItem[] = resp.messages.map((it) => {
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
  return makePagination<DialogueItem[]>(remoteDialogueItems, resp.next_cursor);
};

// --- AttachmentItem ---
export enum AttachmentStatus {
  Pending = 'PENDING',
  Uploaded = 'UPLOADED',
  Indexed = 'INDEXED',
  Errored = 'ERRORED'
}
export type AttachmentItem = {
  status: AttachmentStatus;
  attachment: Attachment;
};

export const pendingAttachmentItem = (attachment: Attachment): AttachmentItem => {
  return {
    status: AttachmentStatus.Pending,
    attachment
  };
};

export const uploadedAttachmentItem = (attachment: Attachment): AttachmentItem => {
  return {
    status: AttachmentStatus.Uploaded,
    attachment
  };
};

export const indexedAttachmentItem = (attachment: Attachment): AttachmentItem => {
  return {
    status: AttachmentStatus.Indexed,
    attachment
  };
};

export const errorAttachmentItem = (attachment: Attachment): AttachmentItem => {
  return {
    status: AttachmentStatus.Errored,
    attachment
  };
};

export const isAttachmentProccesed = (attachment: Attachment): boolean => {
  return (
    attachment.status === AttachmentStatus.Indexed || attachment.status === AttachmentStatus.Errored
  );
};
