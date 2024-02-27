import type { AttachmentUploadRequestPayload } from '$lib/model/request';
import type {
  AttachmentListResponse,
  AttachmentService,
  AttachmentStatus as Attachment
} from '../../generated/client';
import { makeFileRequest, makeRequest, type RequestData } from './request';

function createFormDataFromAttachmentUploadRequestPayload(
  conversationId: string,
  payload: AttachmentUploadRequestPayload
): FormData {
  const formData = new FormData();
  formData.append('id', conversationId);
  formData.append('file', payload.attachment);
  formData.append('company_id', payload.company.id);
  formData.append('sub_sector_id', payload.company.sub_sector_id);
  formData.append('year', payload.year);
  return formData;
}

export function makeAttachmentAPIClient(attachementService: AttachmentService) {
  async function uploadAttachment(conversationId: string, payload: AttachmentUploadRequestPayload) {
    const requestData: RequestData = {
      method: 'POST',
      payload: createFormDataFromAttachmentUploadRequestPayload(conversationId, payload)
    };

    return makeRequest<Attachment>(`/api/conversation/${conversationId}/attachment`, requestData);
  }

  async function getAttachmentStatus(conversationId: string, attachmentId: string) {
    return attachementService.getAttachmentStatusApiConversationIdAttachmentAttachmentIdStatusGet(
      conversationId,
      attachmentId
    );
  }

  async function listAttachments(conversationId: string) {
    return attachementService.listAttachmentsApiConversationIdAttachmentListGet(conversationId);
  }

  async function downloadAttachment(conversationId: string, attachmentId: string) {
    const requestData: RequestData = {
      method: 'GET'
    };
    return makeFileRequest(
      `/api/conversation/${conversationId}/attachment/${attachmentId}`,
      requestData
    );
  }

  async function deleteAttachment(conversationId: string, attachmentId: string) {
    return attachementService.deleteAttachmentApiConversationIdAttachmentAttachmentIdDelete(
      conversationId,
      attachmentId
    );
  }

  async function serverListAttachments(
    serverFetch: (input: RequestInfo, init?: RequestInit) => Promise<Response>,
    conversationId: string
  ) {
    return makeRequest<AttachmentListResponse>(
      `/api/conversation/${conversationId}/attachment/list`,
      {
        method: 'GET'
      },
      serverFetch
    );
  }

  return {
    uploadAttachment,
    getAttachmentStatus,
    listAttachments,
    downloadAttachment,
    deleteAttachment,

    serverListAttachments
  };
}

export type AttachmentAPIClient = ReturnType<typeof makeAttachmentAPIClient>;
