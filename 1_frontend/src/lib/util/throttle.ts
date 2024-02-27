type ThrottledFunction<T> = (arg: T) => void;

export function throttle<T>(func: ThrottledFunction<T>, interval: number): ThrottledFunction<T> {
  let lastExecutionTime = 0;
  let timeout: ReturnType<typeof setTimeout> | null = null;
  let queuedArg: T | null = null;

  const execute = () => {
    if (queuedArg !== null) {
      func(queuedArg);
      lastExecutionTime = Date.now();
      queuedArg = null;
      timeout = setTimeout(execute, interval);
    } else {
      timeout = null;
    }
  };

  return (arg: T) => {
    const currentTime = Date.now();
    if (!timeout) {
      func(arg);
      lastExecutionTime = currentTime;
      timeout = setTimeout(execute, interval);
    } else if (currentTime - lastExecutionTime >= interval) {
      func(arg);
      lastExecutionTime = currentTime;
    } else {
      queuedArg = arg;
    }
  };
}
