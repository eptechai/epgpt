<script lang="ts">
  import { ImgType, getImgPath } from '$lib/util/images';
  import classNames from 'classnames';
  import { Navbar, Dropdown, DropdownItem, DropdownHeader, DropdownDivider } from 'flowbite-svelte';
  import type { UserInfoState } from '../../../stores/userInfoStore';
  import { onDestroy } from 'svelte';
  import { removeLocalStorageItem } from '$lib/util/localStorage';
  import { USER_INFO_LOCAL_STORAGE_KEY } from '$lib/constants';
  import { env } from '$env/dynamic/public';
  import { ContextType, useContexts } from '$lib/context';

  export let isMenuExpanded: boolean;
  export let toggleMenu: () => void;

  const { apiClient, userInfoStore } = useContexts([
    ContextType.API_CLIENT,
    ContextType.USER_INFO_STORE
  ]);

  let userInfoState: UserInfoState;
  const unsubscribe = userInfoStore.subscribe((value) => {
    userInfoState = value;
  });

  let userInitial: string | undefined;
  let email: string | undefined;
  $: {
    userInitial = (userInfoState.userInfo?.email ?? 'debug@example.com').split('@')[0][0] ?? 'U';
    email = userInfoState.userInfo?.email ?? 'debug@example.com';
  }

  const handleLogout = async () => {
    try {
      await apiClient.logout();
    } finally {
      // Note: workaround for Auth0 logout (oauth2 logout redirect doesn't work)
      const link = document.createElement('a');
      link.href = `${env.PUBLIC_AUTH_0_END_SESSION_URL}?client_id=${env.PUBLIC_AUTH_0_CLIENT_ID}&returnTo=${env.PUBLIC_AUTH_0_LOGOUT_REDIRECT_URL}`;
      link.click();
      removeLocalStorageItem(USER_INFO_LOCAL_STORAGE_KEY);
    }
  };

  onDestroy(() => {
    unsubscribe();
  });
</script>

<div class="nav-wrapper">
  <Navbar
    navClass="bg-theme-charcoal px-2 sm:px-4 py-2.5 w-full"
    navDivClass="flex justify-end max-w-full"
  >
    <div id="avatar-menu" class="flex items-center md:order-2">
      <div class="icon-wrapper">
        <div class="icon">{userInitial}</div>
      </div>
    </div>
    <Dropdown class="mr-2" placement="bottom" triggeredBy="#avatar-menu">
      <DropdownHeader>
        <div>User Info</div>
        <span class="block truncate text-sm font-medium">{email}</span>
      </DropdownHeader>
      <DropdownDivider />
      <DropdownItem on:click={handleLogout}>Sign out</DropdownItem>
    </Dropdown>
  </Navbar>
  <button class={classNames('menu-toggle')} on:click={toggleMenu}>
    {#if isMenuExpanded}
      <img src={getImgPath(ImgType.IconChevronLeft)} alt="Collapse" />
    {:else}
      <img src={getImgPath(ImgType.IconChevronRight)} alt="Expand" />
    {/if}
  </button>
</div>

<style lang="scss">
  @import '../../../global.scss';

  .nav-wrapper {
    position: relative;
  }

  .icon-wrapper {
    width: 3rem;
    display: flex;
    flex-direction: column;
    align-self: flex-start;
    cursor: pointer;
  }

  .icon {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 3rem;
    height: 3rem;
    border-radius: 50%;
    background-color: #f2f2f2;
    color: grey;
    font-size: 1.5rem;
    font-weight: bold;
    text-transform: uppercase;
  }

  .menu-toggle {
    color: white;
    font-size: 14px;
    cursor: pointer;

    border-radius: 50%;
    transition: background-color 0.3s ease-in-out, transform 0.2s ease-in-out;
    align-self: flex-end;
    width: 30px;
    height: 30px;
    padding: 4px;
    position: absolute;
    top: 20px;
    left: 8px;
    z-index: 1;

    border: 3px solid $theme-orange;

    &:hover:not(:disabled) {
      cursor: pointer;
      transform: scale(1.1);
      background-color: darken($theme-charcoal, 10%);
    }
  }

  .rotate180 {
    transform: rotate(180deg);
    transition: transform 0.3s ease;
  }
</style>
