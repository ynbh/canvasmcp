
import { tool } from "ai";
import { showGlobalNotificationDataSchema } from "./aitm.schema.ts";
import { showGlobalNotification, ShowGlobalNotificationData } from "..";

export default tool({
  description: `
  Show a global notification
Returns a global notification for the current user
A notification that
has been closed by the user will not be returned
    `,
  parameters: showGlobalNotificationDataSchema.omit({ url: true }),
  execute: async (args : Omit<ShowGlobalNotificationData, "url"> ) => {
    try {
      const { data } = await showGlobalNotification(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    