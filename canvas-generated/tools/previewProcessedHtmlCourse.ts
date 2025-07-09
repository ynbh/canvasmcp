
import { tool } from "ai";
import { previewProcessedHtmlCourseDataSchema } from "./aitm.schema.ts";
import { previewProcessedHtmlCourse, PreviewProcessedHtmlCourseData } from "..";

export default tool({
  description: `
  Preview processed html
Preview html content processed for this course
    `,
  parameters: previewProcessedHtmlCourseDataSchema.omit({ url: true }),
  execute: async (args : Omit<PreviewProcessedHtmlCourseData, "url"> ) => {
    try {
      const { data } = await previewProcessedHtmlCourse(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    