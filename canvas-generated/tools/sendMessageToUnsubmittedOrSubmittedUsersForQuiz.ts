
import { tool } from "ai";
import { sendMessageToUnsubmittedOrSubmittedUsersForQuizDataSchema } from "./aitm.schema.ts";
import { sendMessageToUnsubmittedOrSubmittedUsersForQuiz, SendMessageToUnsubmittedOrSubmittedUsersForQuizData } from "..";

export default tool({
  description: `
  Send a message to unsubmitted or submitted users for the quiz
{
"body": {
"type":
"string",
"description": "message body of the conversation to be created",
"example": "Please take
the quiz."
},
"recipients": {
"type": "string",
"description": "Who to send the message to. May be
either 'submitted' or 'unsubmitted'",
"example": "submitted"
},
"subject": {
"type":
"string",
"description": "Subject of the new Conversation created",
"example": "ATTN: Quiz 101
Students"
}
}
    `,
  parameters: sendMessageToUnsubmittedOrSubmittedUsersForQuizDataSchema.omit({ url: true }),
  execute: async (args : Omit<SendMessageToUnsubmittedOrSubmittedUsersForQuizData, "url"> ) => {
    try {
      const { data } = await sendMessageToUnsubmittedOrSubmittedUsersForQuiz(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    