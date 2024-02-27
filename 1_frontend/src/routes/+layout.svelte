<script lang="ts">
  import '../app.postcss';
  import '../global.scss';
  import '../global-font.scss';
  import { page } from '$app/stores';
  import { ContextType, setGlobalContexts, useContexts } from '$lib/context';
  import Modal from '$lib/component/Modal.svelte';
  import ConfigModalView from '$lib/component/ConfigModalView/ConfigModalView.svelte';
  import SideMenu from '$lib/component/SideMenu/SideMenu.svelte';
  import Navbar from '$lib/component/Navbar/Navbar.svelte';
  import FloatingButtonView from '$lib/component/FloatingButtonView/FloatingButtonView.svelte';
  import classNames from 'classnames';
  import AttachmentDrawer from '$lib/component/AttachmentDrawer/AttachmentDrawer.svelte';
  import { setLocalStorageItem } from '$lib/util/localStorage';
  import { USER_INFO_LOCAL_STORAGE_KEY } from '$lib/constants';
  import ErrorHandler from '$lib/component/ErrorHandler/ErrorHandler.svelte';
  import type { CompanyResponse, SubsectorResponse } from '../generated/client';

  export let data;

  // Note: Contexts
  setGlobalContexts();

  const { conversationListStore, userInfoStore, subSectorCompanyStore } = useContexts([
    ContextType.CONVERSATION_LIST_STORE,
    ContextType.USER_INFO_STORE,
    ContextType.SUBSECTOR_COMPANY_STORE
  ]);
  $: if (data.paginatedConversations) {
    conversationListStore.setConversationList(data.paginatedConversations);
  }
  $: if (data.userInfo) {
    setLocalStorageItem(USER_INFO_LOCAL_STORAGE_KEY, data.userInfo);
    userInfoStore.setUserInfo(data.userInfo);
  }

  $: if (data.subSectorCompanies) {
    const map = data.subSectorCompanies.reduce((acc, it) => {
      acc.set(it, it.companies);
      return acc;
    }, new Map<SubsectorResponse, CompanyResponse[]>());
    subSectorCompanyStore.createNewSubSectorMap(map);
  }

  // Note: Watch for changes in $page.params.id
  let conversationId = $page.params.id;
  let isPendingCreation = false;
  $: {
    conversationId = $page.params.id;
    isPendingCreation = conversationId === undefined;
  }

  /* Component Display Controls */
  // Handle the SideMenu display
  let isMenuExpanded = true;
  const toggleMenu = () => {
    isMenuExpanded = !isMenuExpanded;
  };

  // Handle the modal display
  let showModal = false;
  const handleModalClick = () => {
    showModal = true;
  };
  const handleModalClose = () => {
    showModal = false;
  };

  // Handle the attachment drawer display
  let isDrawerHidden = true;
  const handleAttachmentDrawerClick = () => {
    isDrawerHidden = false;
  };
  const handleAttachmentDrawerClose = () => {
    isDrawerHidden = true;
  };

  let mobileMode = false;
  function dispatchResize() {
    isMenuExpanded = window.innerWidth >= 780;
    mobileMode = window.innerWidth < 540;
  }
</script>

<svelte:window on:resize={dispatchResize} />
<main>
  <div class="main-container">
    <div class="filler" />
    <div class={classNames('wrapper', isMenuExpanded && !mobileMode ? '' : 'slide-content')}>
      <SideMenu isMenuExpanded={isMenuExpanded && !mobileMode} />
      <div
        class={classNames(
          'container-wrapper',
          isMenuExpanded && !mobileMode ? '' : 'slide-content'
        )}
      >
        <Navbar {isMenuExpanded} {toggleMenu} />
        <slot />
      </div>
      <Modal bind:showModal>
        <ConfigModalView onClose={handleModalClose} />
      </Modal>
      <FloatingButtonView
        {mobileMode}
        {isPendingCreation}
        onAttachnmentClick={handleAttachmentDrawerClick}
        onConfigurationClick={handleModalClick}
      />
      {#key conversationId}
        <AttachmentDrawer
          bind:isDrawerHidden
          {conversationId}
          onRequestClose={handleAttachmentDrawerClose}
        />
      {/key}
    </div>
    <ErrorHandler />
  </div>
</main>

<style lang="scss">
  @import '../global.scss';

  .main-container {
    background-image: url('/images/images/Teragonia_Bg_Image_White.png');
    background-size: cover;
    background-repeat: no-repeat;
    background-attachment: fixed;
  }

  .filler {
    width: $side-menu-w;
    height: 68px;
    z-index: 0;
    background-color: $theme-charcoal;
    position: absolute;
    top: 0;
    left: 0;
  }

  .wrapper {
    height: 100vh;
    width: 100vw;
    display: flex;
    flex-direction: row;
    position: relative;

    &.slide-content {
      @include transform(translateX(-$side-menu-w));
      width: calc(100vw + $side-menu-w) !important;
    }
  }

  .menu-toggle {
    color: white;
    font-size: 14px;
    cursor: pointer;

    border-radius: 50%;
    transition: background-color 0.3s ease-in-out;
    align-self: flex-end;
    width: 30px;
    height: 30px;
    padding: 4px;
    position: absolute;
    top: 20px;
    z-index: 1;

    background-color: $theme-stale-grey;

    &:hover:not(:disabled) {
      background-color: darken($theme-stale-grey, 10%);
      cursor: pointer;
    }
  }

  .container-wrapper {
    background-image: url('/images/images/Teragonia_Bg_Image_White.png');
    background-size: cover;
    background-repeat: no-repeat;
    background-attachment: fixed;

    display: flex;
    flex-direction: column;
    background-color: #f9fafb;
    flex: 1;
    overflow: hidden;
    transition: transform 0.2s;
  }
</style>
