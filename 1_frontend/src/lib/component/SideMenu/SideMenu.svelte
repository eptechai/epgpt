<script lang="ts">
  import { page } from '$app/stores';
  import { Sidebar, SidebarGroup, SidebarItem, SidebarWrapper } from 'flowbite-svelte';
  import { onDestroy } from 'svelte';
  import type { ConversationListState } from '../../../stores/conversationListStore';
  import { ImgType, getImgPath } from '$lib/util/images';
  import classNames from 'classnames';
  import { goto } from '$app/navigation';
  import { ContextType, useContexts } from '$lib/context';
  import { PAGINATION_END_TIMESTAMP, makeConversationPagination } from '$lib/util/pagination';
  import Modal from '../Modal.svelte';
  import ConversationDeletionModalView from './ConversationDeletionModalView.svelte';

  export let isMenuExpanded: boolean;
  let activeClass =
    'flex items-center py-1 px-2 text-base font-semibold text-white bg-theme-blue rounded-lg hover:bg-[#524dd8] hover:rounded-lg';
  let nonActiveClass =
    'flex items-center py-1 px-2 text-base font-normal text-white hover:bg-[#243c4f] hover:rounded-lg';

  const { apiClient, conversationListStore, notificationStore } = useContexts([
    ContextType.API_CLIENT,
    ContextType.CONVERSATION_LIST_STORE,
    ContextType.NOTIFICATION_STORE
  ]);

  $: activeUrl = $page.url.pathname;
  $: currentConversationId = $page.params.id;

  let conversationListState: ConversationListState;
  const unsubscribe = conversationListStore.subscribe((value) => {
    conversationListState = value;
  });
  $: conversationList = conversationListState.conversationList.data;

  const handleCreateConversation = () => {
    goto(`/`);
  };

  let listContainer: HTMLDivElement | null = null;
  let isLoadingMore = false;
  const handleOnScroll = () => {
    if (listContainer == null) {
      return;
    }
    if (listContainer.scrollTop + listContainer.clientHeight >= listContainer.scrollHeight - 50) {
      if (isLoadingMore) {
        return;
      }
      loadMore();
    }
  };

  const loadMore = async () => {
    isLoadingMore = true;
    try {
      const nextCursor = conversationListStore.getConversationList().nextCursor;
      if (nextCursor === PAGINATION_END_TIMESTAMP) {
        return;
      }
      const paginatedConversationList = await apiClient.listConversations(nextCursor);
      conversationListStore.appendConversationList(
        makeConversationPagination(paginatedConversationList)
      );
    } catch (e: any) {
      notificationStore.handleError(e, `Failed to load more conversation items: ${e.message}`);
    } finally {
      isLoadingMore = false;
    }
  };

  let hoveredConversationId: string | undefined;
  let pendingDeleteConversationId = currentConversationId;
  let confrimedDeleteConversationId: string | undefined;
  const handleHoverSideMenuItem = (conversationId?: string) => {
    hoveredConversationId = conversationId;
  };

  let showModal = false;
  const triggerDeletion = (conversationId: string) => {
    pendingDeleteConversationId = conversationId;
    showModal = true;
  };
  const closeModal = () => {
    showModal = false;
  };

  const handleDeleteConversation = async (pendingDeleteConversationId: string) => {
    try {
      confrimedDeleteConversationId = pendingDeleteConversationId;
      setTimeout(() => {
        conversationListStore.deleteConversation(pendingDeleteConversationId);
        confrimedDeleteConversationId = undefined;
      }, 500);
      if (currentConversationId === pendingDeleteConversationId) {
        goto('/');
      }
      await apiClient.deleteConversation(pendingDeleteConversationId);
    } catch (e: any) {
      notificationStore.handleError(e, `Failed to delete the conversation: ${e.message}`);
    }
  };

  onDestroy(() => {
    unsubscribe();
  });
</script>

<div class={classNames('side-menu-container', isMenuExpanded ? 'slide-in' : '')}>
  <div class="brand-container">
    <img src={getImgPath(ImgType.InsigniaWhite)} alt="Logo" width={40} />
  </div>
  <div class="new-convo-container">
    <button class="new-convo-button" on:click={handleCreateConversation}>
      <img src={getImgPath(ImgType.IconAdd)} alt="New Conversation" width="18" />
      New Conversation
    </button>
  </div>
  <div on:scroll={handleOnScroll} bind:this={listContainer} class="convo-list-container">
    <Sidebar asideClass="bg-theme-charcoal" {activeUrl} {activeClass} {nonActiveClass}>
      <SidebarWrapper
        divClass="overflow-y-auto py-4 px-3 bg-theme-charcoal rounded dark:bg-gray-800"
      >
        <SidebarGroup>
          <!-- svelte-ignore a11y-no-static-element-interactions -->
          <div class="sidebar-list-view">
            {#each conversationList as conversation}
              <div
                class={classNames(
                  'sidebar-item-wrapper',
                  conversation.id === confrimedDeleteConversationId ? 'fade-leave-to' : ''
                )}
                on:mouseenter={() => {
                  handleHoverSideMenuItem(conversation.id);
                }}
                on:mouseleave={() => {
                  handleHoverSideMenuItem();
                }}
              >
                <SidebarItem
                  spanClass={'truncate ml-3 py-2'}
                  label={conversation.title}
                  href={`/conversations/${conversation.id}`}
                >
                  <svelte:fragment slot="icon">
                    <img src={getImgPath(ImgType.IconChat)} alt="chat" width="20" />
                  </svelte:fragment>
                </SidebarItem>
                {#if hoveredConversationId === conversation.id}
                  <div class="sidebar-item-action-view">
                    <div
                      class={classNames(
                        'sidebar-item-gradiant-view',
                        currentConversationId === conversation.id ? 'selected' : ''
                      )}
                    />
                    <button
                      class={classNames(
                        'sidebar-item-icon-button',
                        currentConversationId === conversation.id ? 'selected' : ''
                      )}
                      on:click={() => {
                        triggerDeletion(conversation.id);
                      }}
                    >
                      <img
                        class="sidebar-delete-icon"
                        src={getImgPath(ImgType.IconDelete)}
                        alt="delete"
                        width={18}
                      />
                    </button>
                  </div>
                {/if}
              </div>
            {/each}
          </div>
        </SidebarGroup>
      </SidebarWrapper>
    </Sidebar>
  </div>
  <Modal bind:showModal>
    <ConversationDeletionModalView
      conversationId={pendingDeleteConversationId}
      onRequestClose={closeModal}
      onDelete={handleDeleteConversation}
    />
  </Modal>
</div>

<style lang="scss">
  @import '../../../global.scss';

  $side-menu-item-h: 48px;

  .side-menu-container {
    // force hardware acceleration in Chrome
    -webkit-transform: translateZ(0);
    -webkit-backface-visibility: hidden;

    width: $side-menu-w;
    min-width: 255px;
    height: 100vh;
    overflow: scroll;
    background-color: $theme-charcoal;
    left: 0;
    z-index: 1;
    position: relative;

    transition: transform 0.2s;
    @include transform(translateX(-$side-menu-w));
    &.slide-in {
      @include transform(translateX(0));
    }
  }

  .side-menu-container::-webkit-scrollbar {
    display: none;
  }

  .sidebar-item-wrapper {
    position: relative;

    height: $side-menu-item-h;

    &.fade-leave-to {
      height: 0;
      opacity: 0;
      transition: opacity 0ms, height 500ms;
    }

    &.fade-enter-in {
      height: $side-menu-item-h;
      opacity: 1;
      transition: opacity 0ms, height 500ms;
    }
  }

  .sidebar-item-action-view {
    position: absolute;
    top: 0;
    right: 0;
    bottom: 0;

    display: flex;
    flex-direction: row;
    justify-content: flex-end;
    align-items: center;
    width: 80px;
    pointer-events: none;

    border-top-right-radius: 8px;
    border-bottom-right-radius: 8px;
  }

  .sidebar-item-gradiant-view {
    flex: 3;
    background: linear-gradient(to right, transparent 5%, $theme-charcoal);
    height: 100%;
    pointer-events: none;

    &.selected {
      background: linear-gradient(to right, transparent 5%, $theme-blue);
    }
  }

  .sidebar-item-icon-button {
    flex: 2;
    height: 100%;

    display: flex;
    flex-direction: row;
    justify-content: center;
    align-items: center;
    background-color: $theme-charcoal;
    border-top-right-radius: 8px;
    border-bottom-right-radius: 8px;
    padding-right: 4px;
    pointer-events: all;

    &.selected {
      background-color: $theme-blue;
    }
  }

  .sidebar-delete-icon {
    &:hover:not(:disabled) {
      transform: scale(1.1);
    }
  }

  .brand-container {
    padding: 16px 12px;
  }

  .new-convo-container {
    display: flex;
    justify-content: center;
    margin: 12px 0 20px;
  }

  .new-convo-button {
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 10px 20px;
    border: 2px solid white;
    border-radius: 12px;
    background-color: transparent;
    color: white;
    font-size: 16px;
    cursor: pointer;
    transition: background-color 0.2s, color 0.2s, border-color 0.2s;
    gap: 8px;
    font-weight: 600;
    width: 85%;

    &:hover {
      background-color: darken($theme-charcoal, 5%);
    }
  }

  .convo-list-container {
    height: calc(100vh - 180px);
    overflow-y: scroll;

    @include custom-scroll-bar();
  }
</style>
