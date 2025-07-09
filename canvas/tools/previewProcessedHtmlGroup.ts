
import { tool } from "ai";
import { previewProcessedHtmlGroupDataSchema } from "./aitm.schema.ts";
import { previewProcessedHtmlGroup, PreviewProcessedHtmlGroupData } from "..";

export default tool({
  description: `
  Preview processed html
Preview html content processed for this group
    `,
  parameters: previewProcessedHtmlGroupDataSchema.omit({ url: true }),
  execute: async (args : Omit<PreviewProcessedHtmlGroupData, "url"> ) => {
    try {
      const { data } = await previewProcessedHtmlGroup(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    