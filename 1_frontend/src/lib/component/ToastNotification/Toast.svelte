<script lang="ts">
  import { Toast } from 'flowbite-svelte';
  import {
    CheckCircleSolid,
    ExclamationCircleSolid,
    CloseCircleSolid
  } from 'flowbite-svelte-icons';
  import { ImgType, getImgPath } from '$lib/util/images';
  import { slide, fly } from 'svelte/transition';
  import { onMount } from 'svelte';
  import { type ToastColor, NotificationType } from './types';
  import { useContexts, ContextType } from '$lib/context';

  const { notificationStore } = useContexts([ContextType.NOTIFICATION_STORE]);

  export let message = '';
  export let notificationType: NotificationType;
  export let id = '';

  let iconClass = 'w-5 h-5 focus:outline-none';

  let className = 'bg-[#FDF6B2] mb-2 px-3 py-3';
  let buttonClass = 'hover:bg-[#fcf28c] dark:hover:bg-gray-700 rounded-lg p-2 focus:ring-0	';
  let color: ToastColor = 'yellow';
  $: {
    if (notificationType === NotificationType.Success) {
      color = 'green';
      className = 'bg-[#DEF7EC] mb-2 px-3 py-3';
      buttonClass = 'hover:bg-[#cbf2e1] dark:hover:bg-gray-700 rounded-lg p-2 focus:ring-0';
    } else if (notificationType === NotificationType.Error) {
      color = 'red';
      className = 'bg-[#FDE8E8] mb-2 px-3 py-3';
      buttonClass = 'hover:bg-[#fbd2d2] dark:hover:bg-gray-700 rounded-lg p-2 focus:ring-0';
    }
  }

  let open = true;

  onMount(() => {
    setTimeout(() => {
      closeNotificaton();
    }, 10000);
  });

  const closeNotificaton = () => {
    open = false;
    notificationStore.removeToastNotification(id);
  };
</script>

<Toast {color} bind:open transition={fly} params={{ duration: 5000 }} class={className}>
  <svelte:fragment slot="icon">
    {#if notificationType === NotificationType.Success}
      <CheckCircleSolid class={iconClass} />
    {:else if notificationType === NotificationType.Error}
      <CloseCircleSolid class={iconClass} />
    {:else}
      <ExclamationCircleSolid class={iconClass} />
    {/if}
  </svelte:fragment>
  {message}
  <button slot="close-button" on:click={closeNotificaton} class={buttonClass}>
    <img src={getImgPath(ImgType.IconModalClose)} alt="Close" width={15} />
  </button>
</Toast>
