
import { tool } from "ai";
import { deletePushNotificationEndpointDataSchema } from "./aitm.schema.ts";
import { deletePushNotificationEndpoint, DeletePushNotificationEndpointData } from "..";

export default tool({
  description: `
  Delete a push notification endpoint
    `,
  parameters: deletePushNotificationEndpointDataSchema.omit({ url: true }),
  execute: async (args : Omit<DeletePushNotificationEndpointData, "url"> ) => {
    try {
      const { data } = await deletePushNotificationEndpoint(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    