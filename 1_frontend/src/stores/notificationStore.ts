import { NotificationType, type ToastNotification } from '$lib/component/ToastNotification/types';
import { v4 as uuid } from 'uuid';
import { writable } from 'svelte/store';

export interface NotificationState {
  toastNotifications: Array<ToastNotification>;
  showForceLogoutModal: boolean;
}

const initialState: NotificationState = {
  toastNotifications: [],
  showForceLogoutModal: false
};

const maxNotificationListLength = 3;

const createNotificationStore = () => {
  const { subscribe, update } = writable<NotificationState>(initialState);

  const handleError = (e: any, message?: string) => {
    if (e.status === 401) {
      update((currentState) => {
        return {
          ...currentState,
          showForceLogoutModal: true
        };
      });
    } else {
      addToastNotification(NotificationType.Error, message ?? e.message ?? 'Something went wrong');
    }
  };

  const handleWarning = (message: string) => {
    addToastNotification(NotificationType.Warning, message);
  };

  const addToastNotification = (notificationType: NotificationType, message: string) => {
    update((currentState) => {
      const currentNotificationList = currentState.toastNotifications;
      const updatedNotificationList = [
        ...currentNotificationList,
        { id: uuid(), category: notificationType, message: message }
      ];

      if (updatedNotificationList.length > maxNotificationListLength) {
        updatedNotificationList.splice(
          0,
          updatedNotificationList.length - maxNotificationListLength
        );
      }

      return {
        ...currentState,
        toastNotifications: updatedNotificationList
      };
    });
  };

  const removeToastNotification = (notificationId: string) => {
    update((currentState) => {
      const currentNotificationList = currentState.toastNotifications;
      const updatedNotificationList = currentNotificationList.filter((it) => {
        return it.id !== notificationId;
      });

      return {
        ...currentState,
        toastNotifications: updatedNotificationList
      };
    });
  };

  return {
    subscribe,
    handleError,
    handleWarning,
    removeToastNotification
  };
};

export const notificationStore = createNotificationStore();
export type NotificationStore = ReturnType<typeof createNotificationStore>;
