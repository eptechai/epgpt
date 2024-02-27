import { writable } from 'svelte/store';
import type { UserInfo } from '$lib/model/user';
import { browser } from '$app/environment';
import { USER_INFO_LOCAL_STORAGE_KEY } from '$lib/constants';
import { getLocalStorageItem } from '$lib/util/localStorage';

export interface UserInfoState {
  userInfo: UserInfo | null;
}

const initialState: UserInfoState = {
  userInfo: null
};

const createUserInfoStore = () => {
  const { set, subscribe } = writable<UserInfoState>(
    browser
      ? {
        userInfo: (getLocalStorageItem(USER_INFO_LOCAL_STORAGE_KEY) as UserInfo) ?? null
      }
      : initialState
  );

  const setUserInfo = (userInfo: UserInfo) => {
    set({ userInfo });
  };

  return {
    subscribe,
    setUserInfo
  };
};

export const userInfoStore = createUserInfoStore();
export type UserInfoStore = ReturnType<typeof createUserInfoStore>;
