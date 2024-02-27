import {
  BadRequestError,
  ChatAppAPIError,
  ForbiddenError,
  InternalServerError,
  UnauthorizedError
} from '$lib/error/error';

const stringifyQueryParams = (queryParams: { [key: string]: any }) => {
  const searchParams = new URLSearchParams();
  Object.entries(queryParams).forEach(([k, v]) => {
    if (v == null) {
      return;
    }
    if (v instanceof Array) {
      v.forEach((it) => searchParams.append(k, it));
    } else {
      searchParams.append(k, v);
    }
  });
  return searchParams.toString();
};

const defaultHeaders = (contentType?: string): { [key: string]: any } => ({
  'Content-Type': contentType,
  Accept: 'application/json'
});

export type RequestData = {
  method?: string;
  payload?: FormData | { [key: string]: any };
  queryParams?: { [key: string]: any };
};

export async function makeRequest<T = any>(
  path: string,
  data: RequestData,
  serverFetch?: (input: RequestInfo, init?: RequestInit) => Promise<Response>
): Promise<T> {
  const contentType = 'application/json';
  const _headers = defaultHeaders(contentType);

  if (data.payload instanceof FormData) {
    // Note: let the browser automatically find out if it's `multipart/form-data`
    // and fill out the boundary for us
    delete _headers['Content-Type'];
  }

  const options: RequestInit = {
    credentials: 'include',
    method: data.method ?? 'GET',
    headers: _headers
  };

  if (data.payload) {
    if (data.payload instanceof FormData) {
      options.body = data.payload;
    } else {
      options.body = JSON.stringify(data.payload);
    }
  }

  let requestInput = path;
  if (data.queryParams) {
    requestInput = `${requestInput}?${stringifyQueryParams(data.queryParams)}`;
  }

  const fetcher = serverFetch ?? fetch;
  const rawResponse = await fetcher(`${requestInput}`, options);
  if (rawResponse.status === 204) {
    return Promise.resolve(undefined as T);
  }

  const response: any = await rawResponse.json();
  handleResponse(response, rawResponse.status);
  return response;
}

export async function makeStreamRequest<T = any>(path: string, data: RequestData): Promise<any> {
  const contentType = 'application/json';
  const _headers = defaultHeaders(contentType);

  if (data.payload instanceof FormData) {
    // Note: let the browser automatically find out if it's `multipart/form-data`
    // and fill out the boundary for us
    delete _headers['Content-Type'];
  }

  const options: RequestInit = {
    method: data.method ?? 'GET',
    headers: _headers
  };

  if (data.payload) {
    if (data.payload instanceof FormData) {
      options.body = data.payload;
    } else {
      options.body = JSON.stringify(data.payload);
    }
  }

  let requestInput = path;
  if (data.queryParams) {
    requestInput = `${requestInput}?${stringifyQueryParams(data.queryParams)}`;
  }

  const rawResponse = await fetch(`${requestInput}`, options);
  if (
    rawResponse.status === 204 ||
    (rawResponse.status === 200 && rawResponse.headers.get('content-length') === '0')
  ) {
    return Promise.resolve(undefined as T);
  }
  handleResponse(rawResponse, rawResponse.status);
  return rawResponse;
}

export async function makeFileRequest(path: string, data: RequestData): Promise<any> {
  const contentType = 'application/json';
  const _headers = defaultHeaders(contentType);

  if (data.payload instanceof FormData) {
    // Note: let the browser automatically find out if it's `multipart/form-data`
    // and fill out the boundary for us
    delete _headers['Content-Type'];
  }

  const options: RequestInit = {
    method: data.method ?? 'GET',
    headers: _headers
  };

  if (data.payload) {
    if (data.payload instanceof FormData) {
      options.body = data.payload;
    } else {
      options.body = JSON.stringify(data.payload);
    }
  }

  let requestInput = path;
  if (data.queryParams) {
    requestInput = `${requestInput}?${stringifyQueryParams(data.queryParams)}`;
  }

  const rawResponse = await fetch(`${requestInput}`, options);
  handleResponse(rawResponse, rawResponse.status);
  return rawResponse.blob();
}

function handleResponse(response: any, statusCode: number) {
  if (statusCode === 400) {
    throw new BadRequestError(response.error ?? 'Bad Request Error');
  }
  if (statusCode === 401) {
    throw new UnauthorizedError(response.error ?? 'Unauthorized Error');
  }
  if (statusCode === 403) {
    throw new ForbiddenError(response.error ?? 'Forbidden Error');
  }
  if (statusCode === 500) {
    throw new InternalServerError(response.error ?? 'Internal Server Error');
  }
  if (response && response.message) {
    throw new ChatAppAPIError(response.message);
  }
}
