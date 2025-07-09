
import { tool } from "ai";
import { deleteModuleDataSchema } from "./aitm.schema.ts";
import { deleteModule, DeleteModuleData } from "..";

export default tool({
  description: `
  Delete module
Delete a module
    `,
  parameters: deleteModuleDataSchema.omit({ url: true }),
  execute: async (args : Omit<DeleteModuleData, "url"> ) => {
    try {
      const { data } = await deleteModule(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    