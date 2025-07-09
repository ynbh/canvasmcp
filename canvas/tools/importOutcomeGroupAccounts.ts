
import { tool } from "ai";
import { importOutcomeGroupAccountsDataSchema } from "./aitm.schema.ts";
import { importOutcomeGroupAccounts, ImportOutcomeGroupAccountsData } from "..";

export default tool({
  description: `
  Import an outcome group
Creates a new subgroup of the outcome group with the same title
and
description as the source group, then creates links in that new subgroup to
the same outcomes
that are linked in the source group. Recurses on the
subgroups of the source group, importing them
each in turn into the new
subgroup.

Allows you to copy organizational structure, but does not
create copies of
the outcomes themselves, only new links.

The source group must be either global,
from the same context as this
outcome group, or from an associated account. The source group cannot
be
the root outcome group of its context.
    `,
  parameters: importOutcomeGroupAccountsDataSchema.omit({ url: true }),
  execute: async (args : Omit<ImportOutcomeGroupAccountsData, "url"> ) => {
    try {
      const { data } = await importOutcomeGroupAccounts(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    