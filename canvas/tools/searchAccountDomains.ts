
import { tool } from "ai";
import { searchAccountDomainsDataSchema } from "./aitm.schema.ts";
import { searchAccountDomains, SearchAccountDomainsData } from "..";

export default tool({
  description: `
  Search account domains
Returns a list of up to 5 matching account domains

Partial match on name /
domain are supported
    `,
  parameters: searchAccountDomainsDataSchema.omit({ url: true }),
  execute: async (args : Omit<SearchAccountDomainsData, "url"> ) => {
    try {
      const { data } = await searchAccountDomains(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    