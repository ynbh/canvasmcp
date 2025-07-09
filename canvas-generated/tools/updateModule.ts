
import { tool } from "ai";
import { updateModuleDataSchema } from "./aitm.schema.ts";
import { updateModule, UpdateModuleData } from "..";

export default tool({
  description: `
  Update a module
Update and return an existing module
    `,
  parameters: updateModuleDataSchema.omit({ url: true }),
  execute: async (args : Omit<UpdateModuleData, "url"> ) => {
    try {
      const { data } = await updateModule(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    