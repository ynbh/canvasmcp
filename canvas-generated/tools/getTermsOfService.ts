
import { tool } from "ai";
import { getTermsOfServiceDataSchema } from "./aitm.schema.ts";
import { getTermsOfService, GetTermsOfServiceData } from "..";

export default tool({
  description: `
  Get the Terms of Service
Returns the terms of service for that account
    `,
  parameters: getTermsOfServiceDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetTermsOfServiceData, "url"> ) => {
    try {
      const { data } = await getTermsOfService(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    