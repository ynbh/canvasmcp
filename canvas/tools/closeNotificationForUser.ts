
import { tool } from "ai";
import { closeNotificationForUserDataSchema } from "./aitm.schema.ts";
import { closeNotificationForUser, CloseNotificationForUserData } from "..";

export default tool({
  description: `
  Close notification for user
If the current user no long wants to see this notification it can be
excused with this call
    `,
  parameters: closeNotificationForUserDataSchema.omit({ url: true }),
  execute: async (args : Omit<CloseNotificationForUserData, "url"> ) => {
    try {
      const { data } = await closeNotificationForUser(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    