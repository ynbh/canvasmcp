
import { tool } from "ai";
import { copyCourseContentDataSchema } from "./aitm.schema.ts";
import { copyCourseContent, CopyCourseContentData } from "..";

export default tool({
  description: `
  Copy course content
DEPRECATED: Please use the {api:ContentMigrationsController#create Content
Migrations API}

Copies content from one course into another. The default is to copy all
course
content. You can control specific types to copy by using either the 'except' option
or the
'only' option.

The response is the same as the course copy status endpoint
    `,
  parameters: copyCourseContentDataSchema.omit({ url: true }),
  execute: async (args : Omit<CopyCourseContentData, "url"> ) => {
    try {
      const { data } = await copyCourseContent(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    