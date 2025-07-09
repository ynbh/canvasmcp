
import { tool } from "ai";
import { createToolFromToolconfigurationAccountsDataSchema } from "./aitm.schema.ts";
import { createToolFromToolconfigurationAccounts, CreateToolFromToolconfigurationAccountsData } from "..";

export default tool({
  description: `
  Create Tool from ToolConfiguration
Creates context_external_tool from attached tool_configuration
of
the provided developer_key if not already present in context.
DeveloperKey must have a
ToolConfiguration to create tool or 404 will be raised.
Will return an existing ContextExternalTool
if one already exists.
    `,
  parameters: createToolFromToolconfigurationAccountsDataSchema.omit({ url: true }),
  execute: async (args : Omit<CreateToolFromToolconfigurationAccountsData, "url"> ) => {
    try {
      const { data } = await createToolFromToolconfigurationAccounts(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    