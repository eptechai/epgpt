<script lang="ts">
  import { ContextType, useContexts } from '$lib/context';
  import {
    MessageItemType,
    type DialogueItem,
    ResponseItemType,
    convertMessageListResponseToPaginatedDialogueItems
  } from '$lib/types';
  import { afterUpdate, onDestroy } from 'svelte';
  import type { UserInfoState } from '../../../stores/userInfoStore';
  import TextRequestMessageCell from './TextRequestMessageCell.svelte';
  import ResponseMessageCell from './ResponseMessageCell.svelte';
  import LoadingCell from './LoadingCell.svelte';
  import { ImgType, getImgPath } from '$lib/util/images';
  import { PAGINATION_END_TIMESTAMP, type Pagination } from '$lib/util/pagination';
  import { page } from '$app/stores';
  import { Spinner } from 'flowbite-svelte';
  import InfiniteScroll from '../InfiniteScroll/InfiniteScroll.svelte';
  import classNames from 'classnames';

  export let conversationId: string;
  export let dialogueList: Pagination<DialogueItem[]>;

  export let streaming: boolean;
  export let onCancelStreaming: () => void;

  const { apiClient, userInfoStore, conversationStore, notificationStore } = useContexts([
    ContextType.API_CLIENT,
    ContextType.USER_INFO_STORE,
    ContextType.CONVERSATION_STORE,
    ContextType.NOTIFICATION_STORE
  ]);

  let userInfoState: UserInfoState;
  const unsubscribeUserInfoStore = userInfoStore.subscribe((value) => {
    userInfoState = value;
  });

  // Note: Watch for changes in userInfo
  let userInitial: string | undefined;
  $: {
    userInitial = (userInfoState.userInfo?.email ?? 'debug@example.com').split('@')[0][0] ?? 'U';
  }

  let lastDialogue: HTMLDivElement | null = null;
  let listContainer: HTMLDivElement | null = null;

  let isInitializing = true;
  let showScrollToBottom = false;

  const loadMore = async () => {
    try {
      const nextCursor = conversationStore.getDialogueItemList(conversationId).nextCursor;
      if (nextCursor === PAGINATION_END_TIMESTAMP) {
        return;
      }
      const paginatedMessageList = await apiClient.listMessages(conversationId, nextCursor);
      conversationStore.prependDialogueItemList(
        conversationId,
        convertMessageListResponseToPaginatedDialogueItems(paginatedMessageList)
      );
    } catch (e: any) {
      notificationStore.handleError(e, `Failed to load more message items: ${e.message}`);
    }
  };

  function handleOnScroll() {
    if (listContainer == null) {
      return;
    }

    // Note: Show Scroll To Bottom Button
    if (lastDialogue) {
      const distanceFromBottom =
        listContainer.scrollHeight - (listContainer.scrollTop + listContainer.clientHeight);
      showScrollToBottom = distanceFromBottom >= 300;
    }
  }

  const initScrollToBottom = () => {
    if (listContainer) {
      listContainer.scrollTop = listContainer.scrollHeight;
      setTimeout(() => {
        isInitializing = false;
      }, 80);
    }
  };
  const pageUnsubscribe = page.subscribe(() => {
    isInitializing = true;
    setTimeout(() => {
      initScrollToBottom();
    }, 0);
  });

  // Note: Scroll To Last Dialogue (on clicking scoll to bottom button)
  function scrollToLastDialogue() {
    if (lastDialogue) {
      lastDialogue.scrollIntoView({ behavior: 'smooth', block: 'end' });
    }
  }

  const rateResponse = async (messageId: string, isFeedbackPositive: boolean | null) => {
    try {
      await apiClient.rateResponse(conversationId, messageId, {
        is_feedback_positive: isFeedbackPositive
      });
    } catch (e: any) {
      notificationStore.handleError(e, `Failed to provide response feedback: ${e.message}`);
    }
  };

  afterUpdate(() => {
    // Note: Auto Scroll
    if (lastDialogue && !showScrollToBottom) {
      const listContainer = lastDialogue.closest('.content');
      if (listContainer) {
        const distanceFromBottom =
          listContainer.scrollHeight - (listContainer.scrollTop + listContainer.clientHeight);
        setTimeout(() => {
          if (lastDialogue) {
            const isNearBottom = distanceFromBottom < lastDialogue.clientHeight + 200;
            if (isNearBottom) {
              lastDialogue.scrollIntoView({ behavior: 'smooth', block: 'end' });
            }
          }
        }, 0);
      }
    }
  });

  onDestroy(() => {
    unsubscribeUserInfoStore();
    pageUnsubscribe();
  });
</script>

{#if isInitializing}
  <div class="loading-view">
    <Spinner size={'12'} />
  </div>
{/if}
<div class={classNames(!showScrollToBottom ? 'content-wrapper' : '')}>
  <div bind:this={listContainer} class="content" on:scroll={handleOnScroll}>
    {#each dialogueList.data as dialogue, index}
      <div bind:this={lastDialogue} data-last-dialogue={index === dialogueList.data.length - 1}>
        {#if dialogue.type === MessageItemType.TextRequestMessage}
          <TextRequestMessageCell {userInitial} item={dialogue} />
        {:else if dialogue.type === ResponseItemType.Response}
          <ResponseMessageCell item={dialogue} {rateResponse} {conversationId} />
        {:else if dialogue.type === ResponseItemType.Loading}
          <LoadingCell />
        {:else if dialogue.type === ResponseItemType.Failure}
          <pre>Failed</pre>
        {/if}
      </div>
    {/each}
    <InfiniteScroll
      reverse={true}
      hasMore={dialogueList.nextCursor !== PAGINATION_END_TIMESTAMP}
      threshold={100}
      on:loadMore={loadMore}
    />
  </div>
</div>
<div class="content-action">
  <div class="content-bottom-action">
    {#if showScrollToBottom}
      <button class="scroll-to-bottom-button" on:click={scrollToLastDialogue}>
        <img src={getImgPath(ImgType.IconScrollToBottom)} alt="Scroll To Bottom" />
      </button>
    {/if}
    {#if streaming}
      <button class="stop-gen-button" on:click={onCancelStreaming}>
        <img width={16} src={getImgPath(ImgType.IconStop)} alt="Stop" />
      </button>
    {/if}
  </div>
</div>

<style lang="scss">
  @import '../../../global.scss';

  .content-wrapper {
    border-bottom-left-radius: 40px;
    border-bottom-right-radius: 40px;
    padding-bottom: 12px;
  }
  .loading-view {
    position: absolute;
    top: 0;
    right: 0;
    bottom: 0;
    left: 0;
    z-index: 2;
    background-color: white;

    display: flex;
    justify-content: center;
    padding-top: 6rem;

    border-bottom-left-radius: 40px;
    border-bottom-right-radius: 40px;
  }

  .content {
    display: flex;
    flex-direction: column;
    height: 100%;
    overflow: scroll;
    flex: 16;
    align-self: flex-start;
    padding: 12px 8px;
    @include custom-scroll-bar();
  }

  .content-action {
    position: absolute;
    bottom: 0;
    right: 0;
    display: flex;
    flex-direction: column;
    justify-content: flex-end;
    align-items: center;
    flex: 1;
    min-width: 70px;
    padding: 24px 8px 0;
  }

  .content-bottom-action {
    display: flex;
    flex-direction: column;
  }

  .stop-gen-button {
    display: flex;
    align-items: center;
    justify-content: center;

    color: white;
    font-size: 14px;
    cursor: pointer;

    border-radius: 50%;
    transition: background-color 0.3s ease-in-out;
    align-self: flex-end;
    width: 40px;
    height: 40px;
    margin-bottom: 12px;

    position: relative;
    padding: 8px;

    background-color: $theme-orchid;
    box-shadow: 0 4px 6px $theme-stale-light-grey;

    &:hover:not(:disabled) {
      background-color: darken($theme-orchid, 10%);
      cursor: pointer;
    }

    &:disabled {
      background-color: $theme-light-grey;
      cursor: not-allowed;
    }
  }

  .scroll-to-bottom-button {
    color: white;
    font-size: 14px;
    cursor: pointer;

    border-radius: 50%;
    transition: background-color 0.3s ease-in-out;
    align-self: flex-end;
    width: 40px;
    height: 40px;
    margin-bottom: 12px;

    position: relative;
    padding: 8px;

    background-color: $theme-stale-grey;
    box-shadow: 0 4px 6px $theme-stale-light-grey;

    &:hover:not(:disabled) {
      background-color: darken($theme-stale-grey, 10%);
      cursor: pointer;
    }

    &:disabled {
      background-color: $theme-light-grey;
      cursor: not-allowed;
    }
  }
</style>
