
import { tool } from "ai";
import { updateGlobalNotificationDataSchema } from "./aitm.schema.ts";
import { updateGlobalNotification, UpdateGlobalNotificationData } from "..";

export default tool({
  description: `
  Update a global notification
Update global notification for an account.
    `,
  parameters: updateGlobalNotificationDataSchema.omit({ url: true }),
  execute: async (args : Omit<UpdateGlobalNotificationData, "url"> ) => {
    try {
      const { data } = await updateGlobalNotification(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    