
import { tool } from "ai";
import { getHelpLinksDataSchema } from "./aitm.schema.ts";
import { getHelpLinks, GetHelpLinksData } from "..";

export default tool({
  description: `
  Get help links
Returns the help links for that account
    `,
  parameters: getHelpLinksDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetHelpLinksData, "url"> ) => {
    try {
      const { data } = await getHelpLinks(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    