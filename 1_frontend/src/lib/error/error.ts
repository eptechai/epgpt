export class SchemaValidationError extends Error {
  constructor(message: string, public errors?: string[]) {
    super(message);
    this.name = 'SchemaValidationError';
  }
}

export class BadRequestError extends Error {
  status = 400;
  constructor(public message: string) {
    super(message);
    this.name = 'BadRequestError';
  }
}

export class ForbiddenError extends Error {
  status = 403;
  constructor(public message: string) {
    super(message);
    this.name = 'Forbidden';
  }
}

export class UnauthorizedError extends Error {
  status = 401;
  constructor(public message: string) {
    super(message);
    this.name = 'Unauthorized';
  }
}

export class InternalServerError extends Error {
  status = 500;
  constructor(public message: string) {
    super(message);
    this.name = 'Internal Server Error';
  }
}

export class ChatAppAPIError extends Error {
  constructor(public message: string) {
    super(message);
    this.name = 'ChatAppAPIError';
  }
}
