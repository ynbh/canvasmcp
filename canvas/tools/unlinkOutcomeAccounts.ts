
import { tool } from "ai";
import { unlinkOutcomeAccountsDataSchema } from "./aitm.schema.ts";
import { unlinkOutcomeAccounts, UnlinkOutcomeAccountsData } from "..";

export default tool({
  description: `
  Unlink an outcome
Unlinking an outcome only deletes the outcome itself if this was the last
link to
the outcome in any group in any context. Aligned outcomes cannot be
deleted; as such, if this is the
last link to an aligned outcome, the
unlinking will fail.
    `,
  parameters: unlinkOutcomeAccountsDataSchema.omit({ url: true }),
  execute: async (args : Omit<UnlinkOutcomeAccountsData, "url"> ) => {
    try {
      const { data } = await unlinkOutcomeAccounts(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    