<script lang="ts">
  import { page } from '$app/stores';
  import { onDestroy, onMount } from 'svelte';
  import { useContexts, ContextType } from '$lib/context';
  import {
    type ConversationState,
    MESSAGE_ID_PLACEHOLDER
  } from '../../../stores/conversationStore';
  import {
    textRequestMessageItem,
    type MessageItem,
    responseItem,
    loadingItem,
    type DialogueItem
  } from '$lib/types';
  import MessageList from '$lib/component/ConversationView/MessageList.svelte';
  import { makePagination, type Pagination } from '$lib/util/pagination';
  import MainActionArea from '$lib/component/MainActionArea/MainActionArea.svelte';
  import { extractConversationIdFromPath } from '$lib/util/url';
  import { notificationStore } from '../../../stores/notificationStore';

  // Note: Contexts
  const { apiClient, conversationListStore, conversationStore, subQuestionListStore } = useContexts(
    [
      ContextType.API_CLIENT,
      ContextType.CONVERSATION_LIST_STORE,
      ContextType.CONVERSATION_STORE,
      ContextType.PARAMETERS_STORE,
      ContextType.SUBQUESTION_LIST_STORE
    ]
  );

  // Note: Store subscriptions
  let conversationState: ConversationState;
  const unsubscribeConversationState = conversationStore.subscribe((value) => {
    conversationState = value;
  });

  // Note: Watch for changes in $page.params.id
  let conversationId = $page.params.id;
  let dialogueList: Pagination<DialogueItem[]>;
  $: {
    conversationId = $page.params.id;
    dialogueList =
      conversationState.dialogueMap.get(conversationId) ?? makePagination<DialogueItem[]>([]);
  }

  const pollSubQuestions = (messageId: string) => {
    const pollInterval = 500;
    let timeoutId: NodeJS.Timeout;

    const poll = () => {
      apiClient
        .getSubQuestions(conversationId, messageId)
        .then((response) => {
          if (response?.subquestions?.length > 0) {
            subQuestionListStore.createSubQuestionList(response.subquestions.map((it) => it.text));
            clearTimeout(timeoutId);
            return;
          }
          timeoutId = setTimeout(poll, pollInterval);
        })
        .catch((e: any) => {
          clearTimeout(timeoutId);
          notificationStore.handleError(e, `Failed to fetch subquestions: ${e.message}`);
        });
    };

    timeoutId = setTimeout(poll, pollInterval);
  };

  let isResponseProcessing = false;
  const submitMessage = async (text: string) => {
    if (isResponseProcessing === true) {
      return;
    }
    isResponseProcessing = true;

    // Note: Update the local conversation title with the first message
    if (dialogueList.data.length === 0) {
      conversationListStore.updateConversation({
        id: conversationId,
        title: text
      });
    }

    let messageItem: MessageItem;
    messageItem = textRequestMessageItem(MESSAGE_ID_PLACEHOLDER, text);
    conversationStore.appendDialogueItem(conversationId, messageItem);

    conversationStore.appendDialogueItem(conversationId, loadingItem());
    try {
      const responseMessageStreamResp = await apiClient.streamMessageCreation(conversationId, text);
      await handleResponseMessageStreamResp(responseMessageStreamResp);
    } catch (e: any) {
      notificationStore.handleError(e, `Failed to submit message: ${e.message}`);
    } finally {
      isResponseProcessing = false;
      conversationStore.removeLoadingItem(conversationId);
      subQuestionListStore.clearSubQuestionList();
    }
  };

  let streaming = false;
  let interuptedStreaming = false;
  let currentStreamingResponseId: string | undefined;
  async function handleResponseMessageStreamResp(response: any) {
    if (!response.body) {
      throw new Error('Streaming not supported');
    }
    streaming = true;
    const reader = response.body.getReader();
    const textDecoder = new TextDecoder();
    let word = '';
    while (streaming && !interuptedStreaming) {
      const { done, value } = await reader.read();
      if (done) {
        break;
      }
      const newWord = textDecoder.decode(value);
      word += filterRegisteredTokens(newWord);
      if (word.includes('<|endofid|>')) {
        const [ids, rest] = word.split('<|endofid|>', 2);

        const [_messageId, _responseId] = ids.split(';', 2);
        currentStreamingResponseId = _responseId;

        pollSubQuestions(currentStreamingResponseId);

        if (rest !== undefined && rest !== '') {
          //Note: Update the buffer with the remaining data
          word = rest;
          handleFirstResponseMessageStreamRespBuffer(_responseId);
        } else {
          continue;
        }
      }
      if (currentStreamingResponseId) {
        if (interuptedStreaming) {
          break;
        }
        conversationStore.updateResponseItemResponse(
          conversationId,
          currentStreamingResponseId,
          word
        );
      }
    }
    streaming = false;
    interuptedStreaming = false;
    currentStreamingResponseId = undefined;
  }

  function handleFirstResponseMessageStreamRespBuffer(responseId: string) {
    //Note: Remove the pending item once the first buffer (responseId) arrived
    conversationStore.updateMessagePlaceholderId(conversationId, responseId);
    conversationStore.removeLoadingItem(conversationId);
    conversationStore.appendDialogueItem(
      conversationId,
      responseItem({
        id: responseId,
        citations: [],
        response: '',
        isFeedbackPositive: null
      })
    );

    apiClient.getMessageCitations(conversationId, responseId).then((resp) => {
      conversationStore.updateLatestResponseItemCitations(conversationId, resp.citations);
    });
  }

  function filterRegisteredTokens(newToken: string) {
    if (newToken.includes('<|endoftext|>')) {
      return newToken.replace('<|endoftext|>', '');
    } else if (newToken.includes('###')) {
      return newToken.replace('###', '');
    } else {
      return newToken;
    }
  }

  async function stopStreamingResponseResult(_conversationId: string) {
    streaming = false;
    try {
      if (currentStreamingResponseId) {
        await apiClient.cancelMessageResponse(_conversationId, currentStreamingResponseId);
      }
    } catch (e: any) {
      notificationStore.handleError(e, `Failed to cancel response streaming: ${e.message}`);
    } finally {
      conversationStore.removeLoadingItem(_conversationId);
      subQuestionListStore.clearSubQuestionList();
    }
  }

  const unsubscribePage = page.subscribe((currentRoute) => {
    const _prevConversationId = conversationId;
    const _currentConversationId = extractConversationIdFromPath(currentRoute.url.pathname);
    if (isResponseProcessing && _currentConversationId !== _prevConversationId) {
      // Note: Switching conversation, reset the streaming state
      interuptedStreaming = true;
      stopStreamingResponseResult(_prevConversationId);
    }
  });

  onMount(() => {
    // Note: Auto Submit
    if (typeof window !== 'undefined' && window.history) {
      const currentState = history.state;
      if (currentState && currentState.inputStr !== undefined) {
        submitMessage(history.state.inputStr);

        delete currentState.inputStr;
        history.replaceState(currentState, '', '');
      }
    }
  });

  onDestroy(() => {
    unsubscribeConversationState();
    unsubscribePage();
  });

  let textareaRef: HTMLTextAreaElement | undefined;
  let maxTextareaHeightDelta = 74;
  let errorViewDelta = 0;
  $: {
    errorViewDelta = 0;
  }
  function updateMaxHeightDelta(textareaDelta: number) {
    maxTextareaHeightDelta = Math.max(
      Math.min(textareaDelta + errorViewDelta + 60, 276 + errorViewDelta),
      74
    );
  }
</script>

<div class="container">
  <div class="content-wrapper" style="max-height: calc(100vh - {maxTextareaHeightDelta}px - 60px)">
    {#key conversationId}
      <MessageList
        {conversationId}
        {dialogueList}
        {streaming}
        onCancelStreaming={() => {
          stopStreamingResponseResult(conversationId);
        }}
      />
    {/key}
  </div>
  <div class="action-wrapper">
    <MainActionArea
      disableNewMsg={streaming || isResponseProcessing}
      {textareaRef}
      {updateMaxHeightDelta}
      onSubmit={submitMessage}
    />
  </div>
</div>

<style lang="scss">
  @import '../../../global.scss';

  .container {
    display: flex;
    flex-direction: column;
    align-items: center;
    height: 100vh;
    flex: 3;
    margin: 0 auto;

    @media screen and (max-width: 2000px) {
      padding: 0 5rem;
    }

    @media screen and (max-width: 540px) {
      padding: 0;
    }
  }

  .content-wrapper {
    display: flex;
    flex-direction: row;
    height: 100%;
    width: 100%;
    background-color: #f9fafb;
    margin-bottom: 20px;
    position: relative;

    box-shadow: 0 4px 6px $theme-stale-light-grey;
    border-bottom-left-radius: 40px;
    border-bottom-right-radius: 40px;
  }

  .action-wrapper {
    width: 100%;
    margin-bottom: 16px;
  }
</style>
