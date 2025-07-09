
import { tool } from "ai";
import { deleteOutcomeGroupAccountsDataSchema } from "./aitm.schema.ts";
import { deleteOutcomeGroupAccounts, DeleteOutcomeGroupAccountsData } from "..";

export default tool({
  description: `
  Delete an outcome group
Deleting an outcome group deletes descendant outcome groups and
outcome
links. The linked outcomes themselves are only deleted if all links to the
outcome were
deleted.

Aligned outcomes cannot be deleted; as such, if all remaining links to an
aligned outcome
are included in this group's descendants, the group
deletion will fail.
    `,
  parameters: deleteOutcomeGroupAccountsDataSchema.omit({ url: true }),
  execute: async (args : Omit<DeleteOutcomeGroupAccountsData, "url"> ) => {
    try {
      const { data } = await deleteOutcomeGroupAccounts(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    