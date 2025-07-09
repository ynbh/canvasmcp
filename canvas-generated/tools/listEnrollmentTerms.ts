
import { tool } from "ai";
import { listEnrollmentTermsDataSchema } from "./aitm.schema.ts";
import { listEnrollmentTerms, ListEnrollmentTermsData } from "..";

export default tool({
  description: `
  List enrollment terms
A paginated list of all of the terms in the account.
    `,
  parameters: listEnrollmentTermsDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListEnrollmentTermsData, "url"> ) => {
    try {
      const { data } = await listEnrollmentTerms(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    