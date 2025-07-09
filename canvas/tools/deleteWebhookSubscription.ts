
import { tool } from "ai";
import { deleteWebhookSubscriptionDataSchema } from "./aitm.schema.ts";
import { deleteWebhookSubscription, DeleteWebhookSubscriptionData } from "..";

export default tool({
  description: `
  Delete a Webhook Subscription
    `,
  parameters: deleteWebhookSubscriptionDataSchema.omit({ url: true }),
  execute: async (args : Omit<DeleteWebhookSubscriptionData, "url"> ) => {
    try {
      const { data } = await deleteWebhookSubscription(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    