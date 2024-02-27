<script lang="ts">
  import { ContextType, useContexts } from '$lib/context';
  import { env } from '$env/dynamic/public';
  import { removeLocalStorageItem } from '$lib/util/localStorage';
  import { USER_INFO_LOCAL_STORAGE_KEY } from '$lib/constants';

  const { apiClient } = useContexts([ContextType.API_CLIENT]);

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

  const handleKeepSession = () => {
    if (window && window.location) {
      window.location.reload();
    }
  };
</script>

<div>
  <div class="title-container">
    <div class="title">Your Session Has Expired Due to Inactivity</div>
  </div>
  <div class="content">
    <p class="content-text">Please select keep session or log in again to continue.</p>
  </div>
  <div class="actions">
    <button class="keep-session-button" on:click={handleKeepSession}>Keep Session</button>
    <button class="logout-button" on:click={handleLogout}>Log Out</button>
  </div>
</div>

<style lang="scss">
  @import '../../../global.scss';

  .title-container {
    display: flex;
    align-items: center;
    margin-bottom: 12px;
  }

  .title {
    font-size: 18px;
    font-weight: 600;
    color: $theme-charcoal;
  }

  .table-container {
    max-height: calc(100vh - 16rem);
    overflow-y: auto;

    @include custom-scroll-bar();
  }

  .actions {
    display: flex;
    flex-direction: row;
    justify-content: flex-end;
    width: 100%;
    margin-top: 32px;
    gap: 16px;
  }

  .content {
    padding: 16px;
  }

  .content-text {
    font-size: 16px;
    color: $theme-charcoal;
    line-height: 1.5;
  }

  .keep-session-button {
    background-color: $theme-blue;
    color: white;
    border-radius: 4px;
    padding: 10px 16px;
    font-size: 16px;

    &:hover:not(:disabled) {
      background-color: darken($theme-blue, 10%);
      cursor: pointer;
    }
  }

  .logout-button {
    background-color: red;
    color: white;
    border-radius: 4px;
    padding: 10px 16px;
    font-size: 16px;

    &:hover:not(:disabled) {
      background-color: darken(red, 10%);
      cursor: pointer;
    }
  }
</style>
