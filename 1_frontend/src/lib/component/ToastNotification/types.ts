export type ToastColor =
  | 'gray'
  | 'red'
  | 'yellow'
  | 'green'
  | 'indigo'
  | 'purple'
  | 'blue'
  | 'primary'
  | 'orange'
  | 'none'
  | undefined;

export enum NotificationType {
  Success = 'Success',
  Error = 'Error',
  Warning = 'Warning'
}

export type ToastNotification = {
  id: string;
  category: NotificationType;
  message: string;
};
