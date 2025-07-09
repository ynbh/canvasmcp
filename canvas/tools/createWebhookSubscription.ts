
import { tool } from "ai";
import { createWebhookSubscriptionDataSchema } from "./aitm.schema.ts";
import { createWebhookSubscription, CreateWebhookSubscriptionData } from "..";

export default tool({
  description: `
  Create a Webhook Subscription
Creates a webook subscription for the specified event type
and
context.
    `,
  parameters: createWebhookSubscriptionDataSchema.omit({ url: true }),
  execute: async (args : Omit<CreateWebhookSubscriptionData, "url"> ) => {
    try {
      const { data } = await createWebhookSubscription(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    