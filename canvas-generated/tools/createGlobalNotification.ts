
import { tool } from "ai";
import { createGlobalNotificationDataSchema } from "./aitm.schema.ts";
import { createGlobalNotification, CreateGlobalNotificationData } from "..";

export default tool({
  description: `
  Create a global notification
Create and return a new global notification for an account.
    `,
  parameters: createGlobalNotificationDataSchema.omit({ url: true }),
  execute: async (args : Omit<CreateGlobalNotificationData, "url"> ) => {
    try {
      const { data } = await createGlobalNotification(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    