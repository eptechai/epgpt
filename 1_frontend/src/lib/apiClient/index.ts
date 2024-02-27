import { FastAPIClient } from '../../generated/client';
import { makeAttachmentAPIClient, type AttachmentAPIClient } from './attachment';
import { makeConversationAPIClient, type ConversationAPIClient } from './conversation';
import { makeMessageAPIClient, type MessageAPIClient } from './message';
import { makeUserAPIClient, type UserAPIClient } from './user';
import { makeCompanyAPIClient, type CompanyAPIClient } from './company';
import { makeDocumentAPIClient, type DocumentAPIClient } from './document';
import { makeSubSectorAPIClient, type SubSectorAPIClient } from './subsector';

export type APIClient = ConversationAPIClient &
  MessageAPIClient &
  AttachmentAPIClient &
  CompanyAPIClient &
  DocumentAPIClient &
  SubSectorAPIClient &
  UserAPIClient;

export const makeAPIClient = (): APIClient => {
  const fastAPIClient = new FastAPIClient({
    CREDENTIALS: 'include'
  });

  return {
    ...makeConversationAPIClient(fastAPIClient.conversation),
    ...makeMessageAPIClient(fastAPIClient.message),
    ...makeAttachmentAPIClient(fastAPIClient.attachment),
    ...makeCompanyAPIClient(fastAPIClient.company),
    ...makeDocumentAPIClient(),
    ...makeSubSectorAPIClient(fastAPIClient.subSector),
    ...makeUserAPIClient()
  };
};

export default makeAPIClient;
