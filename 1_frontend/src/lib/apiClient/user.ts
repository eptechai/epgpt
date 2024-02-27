import type { UserInfo } from '$lib/model/user';
import { makeRequest, type RequestData } from './request';

export function makeUserAPIClient() {
  async function serverGetUserInfo(
    serverFetch?: (input: RequestInfo, init?: RequestInit) => Promise<Response>
  ) {
    const requestData: RequestData = {
      method: 'GET'
    };

    return makeRequest<UserInfo>(`/oauth2/userinfo`, requestData, serverFetch);
  }

  async function logout() {
    const requestData: RequestData = {
      method: 'GET'
    };

    return makeRequest(`/oauth2/sign_out`, requestData);
  }

  return {
    serverGetUserInfo,
    logout
  };
}

export type UserAPIClient = ReturnType<typeof makeUserAPIClient>;
