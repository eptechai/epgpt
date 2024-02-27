<script lang="ts">
  import EmptyConversationView from '$lib/component/EmptyConversationView/EmptyConversationView.svelte';
  import { CONVO_PENDING_CREATION_ID, medicalSampleQuestions } from '$lib/constants';
  import MainActionArea from '$lib/component/MainActionArea/MainActionArea.svelte';
  import { ContextType, useContexts } from '$lib/context';
  import { goto } from '$app/navigation';
  import type { Conversation } from '../generated/client';

  const { apiClient, conversationListStore, parametersStore, notificationStore } = useContexts([
    ContextType.API_CLIENT,
    ContextType.CONVERSATION_LIST_STORE,
    ContextType.PARAMETERS_STORE,
    ContextType.NOTIFICATION_STORE
  ]);

  let selectedSampleQuestion: string | undefined = undefined;

  // Note: Handle main action submission
  const handleMainActionSubmission = async (text: string) => {
    const newConversation = await createNewConversation();
    selectedSampleQuestion = undefined;

    if (!newConversation) {
      return;
    }
    conversationListStore.appendConversation(newConversation);
    goto(`/conversations/${newConversation.id}`, {
      state: {
        inputStr: text
      }
    });
  };

  const createNewConversation = async (): Promise<Conversation | undefined> => {
    try {
      const conversationResponse = await apiClient.createConversation();
      const conversation: Conversation = {
        id: conversationResponse.conversation_id,
        title: conversationResponse.conversation_id
      };

      // Note: Apply the pending parameters to the conversation
      const paramsResp = await apiClient.updateConversationParams(
        conversation.id,
        parametersStore.getParamsResponse(CONVO_PENDING_CREATION_ID)
      );
      parametersStore.setRemoteParameters(conversation.id, paramsResp);

      // Note: Inherit the configurable parameters from the pending state
      parametersStore.setConfigurableParameterOptions(
        conversation.id,
        parametersStore.getConfigurableParameterOptions(CONVO_PENDING_CREATION_ID)
      );

      // Note: Reset the pending parameters
      parametersStore.resetState(CONVO_PENDING_CREATION_ID);
      return conversation;
    } catch (e: any) {
      notificationStore.handleError(e, `Error creating conversation: ${e.message}`);
    }
  };

  async function onSubmitSampleQuestion(text: string) {
    selectedSampleQuestion = text;
    await handleMainActionSubmission(text);
  }

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
    <EmptyConversationView
      {selectedSampleQuestion}
      sampleQuestions={medicalSampleQuestions}
      onSuggestionClick={onSubmitSampleQuestion}
    />
  </div>
  <div class="action-wrapper">
    <MainActionArea {textareaRef} {updateMaxHeightDelta} onSubmit={handleMainActionSubmission} />
  </div>
</div>

<style lang="scss">
  @import '../global.scss';

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
