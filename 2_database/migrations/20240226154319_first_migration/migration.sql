-- CreateEnum
CREATE TYPE "ConversationStatus" AS ENUM ('IDLE', 'BUSY');

-- CreateEnum
CREATE TYPE "AttachmentStatus" AS ENUM ('PENDING', 'UPLOADED', 'INDEXED', 'ERRORED');

-- CreateEnum
CREATE TYPE "MessageAuthor" AS ENUM ('USER', 'BOT');

-- CreateEnum
CREATE TYPE "ConversationPermissionRole" AS ENUM ('OWNER');

-- CreateEnum
CREATE TYPE "CompanyOwner" AS ENUM ('GLOBAL', 'USER');

-- CreateEnum
CREATE TYPE "DocumentSource" AS ENUM ('CORPUS', 'USER_UPLOADED');

-- CreateTable
CREATE TABLE "Conversation" (
    "id" TEXT NOT NULL,
    "title" TEXT NOT NULL DEFAULT 'Untitled Conversation',
    "parameters" JSONB NOT NULL,
    "vectorDbPath" TEXT,
    "status" "ConversationStatus" NOT NULL,
    "created_At" BIGINT NOT NULL DEFAULT extract(epoch from now()),
    "updated_At" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "Conversation_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "Tag" (
    "id" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "createdAt" BIGINT NOT NULL DEFAULT extract(epoch from now()),
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "Tag_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "TagOnAttachment" (
    "id" TEXT NOT NULL,
    "tagId" TEXT NOT NULL,
    "attachmentId" TEXT NOT NULL,
    "createdAt" BIGINT NOT NULL DEFAULT extract(epoch from now()),
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "TagOnAttachment_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "Attachment" (
    "id" TEXT NOT NULL,
    "status" "AttachmentStatus" NOT NULL DEFAULT 'PENDING',
    "createdAt" BIGINT NOT NULL DEFAULT extract(epoch from now()),
    "updatedAt" TIMESTAMP(3) NOT NULL,
    "documentId" TEXT NOT NULL,
    "companyId" TEXT NOT NULL,
    "subSectorId" TEXT NOT NULL,
    "year" INTEGER NOT NULL,

    CONSTRAINT "Attachment_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "Message" (
    "id" TEXT NOT NULL,
    "author" "MessageAuthor" NOT NULL,
    "text" TEXT NOT NULL,
    "conversationId" TEXT NOT NULL,
    "createdAt" BIGINT NOT NULL DEFAULT extract(epoch from now()),
    "updatedAt" TIMESTAMP(3) NOT NULL,
    "isFeedbackPositive" BOOLEAN,

    CONSTRAINT "Message_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "Citation" (
    "id" TEXT NOT NULL,
    "content" TEXT NOT NULL,
    "pageNumber" INTEGER NOT NULL,
    "fileName" TEXT NOT NULL,
    "messageId" TEXT NOT NULL,
    "createdAt" BIGINT NOT NULL DEFAULT extract(epoch from now()),
    "updatedAt" TIMESTAMP(3) NOT NULL,
    "documentId" TEXT NOT NULL,

    CONSTRAINT "Citation_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "ConversationPermission" (
    "id" TEXT NOT NULL,
    "conversationId" TEXT NOT NULL,
    "userId" TEXT NOT NULL,
    "role" "ConversationPermissionRole" NOT NULL,
    "createdAt" BIGINT NOT NULL DEFAULT extract(epoch from now()),
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "ConversationPermission_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "SubQuestion" (
    "id" TEXT NOT NULL,
    "text" TEXT NOT NULL,
    "response" TEXT NOT NULL,
    "toolName" TEXT NOT NULL,
    "messageId" TEXT NOT NULL,

    CONSTRAINT "SubQuestion_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "Company" (
    "id" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "toolName" TEXT NOT NULL,
    "subSectorId" TEXT NOT NULL,
    "owner" "CompanyOwner" NOT NULL,
    "userId" TEXT,
    "createdAt" BIGINT NOT NULL DEFAULT extract(epoch from now()),

    CONSTRAINT "Company_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "SubSector" (
    "id" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "owner" "CompanyOwner" NOT NULL,
    "userId" TEXT,

    CONSTRAINT "SubSector_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "Document" (
    "id" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "source" "DocumentSource" NOT NULL,
    "link" TEXT NOT NULL,
    "credentials" TEXT NOT NULL,
    "conversationId" TEXT,

    CONSTRAINT "Document_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "Attachment_documentId_key" ON "Attachment"("documentId");

-- CreateIndex
CREATE UNIQUE INDEX "Company_name_key" ON "Company"("name");

-- CreateIndex
CREATE UNIQUE INDEX "SubSector_name_key" ON "SubSector"("name");

-- AddForeignKey
ALTER TABLE "TagOnAttachment" ADD CONSTRAINT "TagOnAttachment_tagId_fkey" FOREIGN KEY ("tagId") REFERENCES "Tag"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "TagOnAttachment" ADD CONSTRAINT "TagOnAttachment_attachmentId_fkey" FOREIGN KEY ("attachmentId") REFERENCES "Attachment"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Attachment" ADD CONSTRAINT "Attachment_documentId_fkey" FOREIGN KEY ("documentId") REFERENCES "Document"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Attachment" ADD CONSTRAINT "Attachment_companyId_fkey" FOREIGN KEY ("companyId") REFERENCES "Company"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Attachment" ADD CONSTRAINT "Attachment_subSectorId_fkey" FOREIGN KEY ("subSectorId") REFERENCES "SubSector"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Message" ADD CONSTRAINT "Message_conversationId_fkey" FOREIGN KEY ("conversationId") REFERENCES "Conversation"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Citation" ADD CONSTRAINT "Citation_messageId_fkey" FOREIGN KEY ("messageId") REFERENCES "Message"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Citation" ADD CONSTRAINT "Citation_documentId_fkey" FOREIGN KEY ("documentId") REFERENCES "Document"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "ConversationPermission" ADD CONSTRAINT "ConversationPermission_conversationId_fkey" FOREIGN KEY ("conversationId") REFERENCES "Conversation"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "SubQuestion" ADD CONSTRAINT "SubQuestion_messageId_fkey" FOREIGN KEY ("messageId") REFERENCES "Message"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Company" ADD CONSTRAINT "Company_subSectorId_fkey" FOREIGN KEY ("subSectorId") REFERENCES "SubSector"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Document" ADD CONSTRAINT "Document_conversationId_fkey" FOREIGN KEY ("conversationId") REFERENCES "Conversation"("id") ON DELETE CASCADE ON UPDATE CASCADE;
