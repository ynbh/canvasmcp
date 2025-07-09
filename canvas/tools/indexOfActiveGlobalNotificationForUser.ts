
import { tool } from "ai";
import { indexOfActiveGlobalNotificationForUserDataSchema } from "./aitm.schema.ts";
import { indexOfActiveGlobalNotificationForUser, IndexOfActiveGlobalNotificationForUserData } from "..";

export default tool({
  description: `
  Index of active global notification for the user
Returns a list of all global notifications in the
account for the current user
Any notifications that have been closed by the user will not be
returned
    `,
  parameters: indexOfActiveGlobalNotificationForUserDataSchema.omit({ url: true }),
  execute: async (args : Omit<IndexOfActiveGlobalNotificationForUserData, "url"> ) => {
    try {
      const { data } = await indexOfActiveGlobalNotificationForUser(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    