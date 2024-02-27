<script lang="ts">
  import Toast from '../ToastNotification/Toast.svelte';
  import type { NotificationState } from '../../../stores/notificationStore';
  import { useContexts, ContextType } from '$lib/context';
  import { onDestroy } from 'svelte';
  import Modal from '../Modal.svelte';
  import ForceLogoutModal from '../ForceLogoutModalView/ForceLogoutModal.svelte';

  const { notificationStore } = useContexts([ContextType.NOTIFICATION_STORE]);

  let notificationState: NotificationState;
  const unsubscribe = notificationStore.subscribe((value) => {
    notificationState = value;
  });
  $: toastNotifications = notificationState.toastNotifications;
  $: showForceLogoutModal = notificationState.showForceLogoutModal;

  onDestroy(() => {
    unsubscribe();
  });
</script>

<div class="toast-wrapper">
  {#each toastNotifications as toastMessage (toastMessage.id)}
    <Toast
      id={toastMessage.id}
      notificationType={toastMessage.category}
      message={toastMessage.message}
    />
  {/each}
</div>
<Modal bind:showModal={showForceLogoutModal} dismissable={false}>
  <ForceLogoutModal />
</Modal>

<style lang="scss">
  .toast-wrapper {
    position: fixed;
    top: 7px;
    width: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    z-index: 1000;
  }
</style>
