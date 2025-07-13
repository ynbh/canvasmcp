import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

// Import existing Canvas tools
import listFavoriteCourses from './canvas-generated/tools/listFavoriteCourses.ts';
import listFilesCourses from './canvas-generated/tools/listFilesCourses.ts';
import listAllFoldersCourses from './canvas-generated/tools/listAllFoldersCourses.ts';
import listAssignments from './canvas-generated/tools/listAssignments.ts';
import listAssignmentIDs from './canvas-generated/tools/listAssignmentIDs.ts';
import getSingleAssignment from './canvas-generated/tools/getSingleAssignment.ts';
import listCalendarEvents from './canvas-generated/tools/listCalendarEvents.ts';
import listAnnouncements from './canvas-generated/tools/listAnnouncements.ts';
import listUsersInCourseUsers from './canvas-generated/tools/listUsersInCourseUsers.ts';
import getCurrentDate from './canvas-generated/tools/getCurrentDate.ts';

// Context management (same as chat mode)
let courseContext = new Map<string, string>(); // Map<courseId, courseName>
let assignmentCache = new Map<string, {courseId: string, name: string}>(); // Map<assignmentId, {courseId, name}>

// Create MCP server
const server = new McpServer({
  name: "canvas-lms-ai",
  version: "1.0.0"
});

// Register Canvas tools as MCP tools

server.registerTool(
  "get_current_date",
  {
    title: "Get Current Date",
    description: "Get current date and time for filtering assignments and calendar events by due dates",
    inputSchema: {}
  },
  async () => {
    try {
      const result = await getCurrentDate.execute({});
      return {
        content: [{ type: "text", text: JSON.stringify(result, null, 2) }]
      };
    } catch (error: any) {
      return {
        content: [{ type: "text", text: `Error: ${error.message}` }],
        isError: true
      };
    }
  }
);

server.registerTool(
  "list_favorite_courses", 
  {
    title: "List Favorite Courses",
    description: "Get starred/favorited Canvas courses. These are courses the user has marked as favorites in Canvas",
    inputSchema: {}
  },
  async () => {
    try {
      const { data } = await listFavoriteCourses.execute({});
      
      // Cache course context (same logic as chat mode)
      if (Array.isArray(data)) {
        data.forEach(course => {
          if (typeof course === 'object' && course !== null && 'id' in course && course.id && course.name) {
            courseContext.set(course.id.toString(), course.name);
          }
        });
      }
      
      return {
        content: [{ type: "text", text: JSON.stringify(data, null, 2) }]
      };
    } catch (error: any) {
      return {
        content: [{ type: "text", text: `Error: ${error.message}` }],
        isError: true
      };
    }
  }
);

server.registerTool(
  "get_course_context",
  {
    title: "Get Course Context", 
    description: "Returns known course IDs/names and recently seen assignment IDs/names from prior interactions. Use this to check existing context before making other API calls",
    inputSchema: {}
  },
  async () => {
    try {
      const result = {
        courses: Array.from(courseContext.entries()).map(([id, name]) => ({ id, name })),
        assignments: Array.from(assignmentCache.entries()).map(([assignmentId, data]) => ({
          assignmentId,
          courseId: data.courseId,
          name: data.name
        }))
      };
      return {
        content: [{ type: "text", text: JSON.stringify(result, null, 2) }]
      };
    } catch (error: any) {
      return {
        content: [{ type: "text", text: `Error: ${error.message}` }],
        isError: true
      };
    }
  }
);

server.registerTool(
  "list_assignments",
  {
    title: "List Course Assignments",
    description: "Get assignments for a specific course. Supports filtering by bucket (past, upcoming, overdue, etc.)",
    inputSchema: {
      courseId: z.string().describe("Canvas course ID"),
      bucket: z.enum(["past", "overdue", "undated", "ungraded", "unsubmitted", "upcoming", "future"]).optional().describe("Filter assignments by status bucket"),
      include: z.array(z.enum(["submission", "assignment_visibility", "all_dates", "overrides", "observed_users"])).optional().describe("Additional data to include")
    }
  },
  async ({ courseId, bucket, include }) => {
    try {
      const args: any = {
        path: { course_id: courseId }
      };
      
      if (bucket || include) {
        args.query = {};
        if (bucket) args.query.bucket = bucket;
        if (include) args.query.include = include;
      }
      
      const { data } = await listAssignments.execute(args);
      
      // Cache assignment context (same logic as chat mode)
      if (Array.isArray(data)) {
        data.forEach(assignment => {
          if (typeof assignment === 'object' && assignment !== null && 'id' in assignment && assignment.id && assignment.name) {
            assignmentCache.set(assignment.id.toString(), {
              courseId: courseId.toString(),
              name: assignment.name
            });
          }
        });
      }
      
      return {
        content: [{ type: "text", text: JSON.stringify(data, null, 2) }]
      };
    } catch (error: any) {
      return {
        content: [{ type: "text", text: `Error: ${error.message}` }],
        isError: true
      };
    }
  }
);

server.registerTool(
  "get_assignment_details",
  {
    title: "Get Assignment Details",
    description: "Get detailed information about a specific assignment including description, submission types, points, rubric info, and requirements",
    inputSchema: {
      courseId: z.string().describe("Canvas course ID"),
      assignmentId: z.string().describe("Canvas assignment ID"),
      include: z.array(z.enum(["submission", "assignment_visibility", "overrides", "observed_users"])).optional().describe("Additional data to include")
    }
  },
  async ({ courseId, assignmentId, include }) => {
    try {
      const args: any = {
        path: { 
          course_id: courseId,
          id: assignmentId 
        }
      };
      
      if (include) {
        args.query = { include };
      }
      
      const result = await getSingleAssignment.execute(args);
      
      // Cache assignment context
      if (result && typeof result === 'object' && 'id' in result && result.id && result.name) {
        assignmentCache.set(result.id.toString(), {
          courseId: courseId.toString(),
          name: result.name
        });
      }
      
      return {
        content: [{ type: "text", text: JSON.stringify(result, null, 2) }]
      };
    } catch (error: any) {
      return {
        content: [{ type: "text", text: `Error: ${error.message}` }],
        isError: true
      };
    }
  }
);

server.registerTool(
  "list_course_files",
  {
    title: "List Course Files",
    description: "Get files for a specific course with pagination support",
    inputSchema: {
      courseId: z.string().describe("Canvas course ID"),
      page: z.string().optional().describe("Page number for pagination"),
      perPage: z.number().optional().describe("Number of items per page")
    }
  },
  async ({ courseId, page, perPage }) => {
    try {
      const args: any = {
        path: { course_id: courseId }
      };
      
      if (page || perPage) {
        args.query = {};
        if (page) args.query.page = page;
        if (perPage) args.query.per_page = perPage;
      }
      
      const { data } = await listFilesCourses.execute(args);
      return {
        content: [{ type: "text", text: JSON.stringify(data, null, 2) }]
      };
    } catch (error: any) {
      return {
        content: [{ type: "text", text: `Error: ${error.message}` }],
        isError: true
      };
    }
  }
);

server.registerTool(
  "list_course_folders", 
  {
    title: "List Course Folders",
    description: "Get all folders for a specific course",
    inputSchema: {
      courseId: z.string().describe("Canvas course ID")
    }
  },
  async ({ courseId }) => {
    try {
      const { data } = await listAllFoldersCourses.execute({
        path: { course_id: courseId }
      });
      return {
        content: [{ type: "text", text: JSON.stringify(data, null, 2) }]
      };
    } catch (error: any) {
      return {
        content: [{ type: "text", text: `Error: ${error.message}` }],
        isError: true
      };
    }
  }
);

server.registerTool(
  "list_calendar_events",
  {
    title: "List Calendar Events", 
    description: "Get calendar events, which may include assignment due dates and other course events",
    inputSchema: {
      type: z.enum(["event", "assignment"]).optional().describe("Filter by event type"),
      startDate: z.string().optional().describe("Start date filter (ISO format)"),
      endDate: z.string().optional().describe("End date filter (ISO format)"),
      contextCodes: z.array(z.string()).optional().describe("Context codes to filter by (e.g., course_123)")
    }
  },
  async ({ type, startDate, endDate, contextCodes }) => {
    try {
      const args: any = {};
      const query: any = {};
      
      if (type) query.type = type;
      if (startDate) query.start_date = startDate;
      if (endDate) query.end_date = endDate;
      if (contextCodes) query.context_codes = contextCodes;
      
      if (Object.keys(query).length > 0) {
        args.query = query;
      }
      
      const { data } = await listCalendarEvents.execute(args);
      return {
        content: [{ type: "text", text: JSON.stringify(data, null, 2) }]
      };
    } catch (error: any) {
      return {
        content: [{ type: "text", text: `Error: ${error.message}` }],
        isError: true
      };
    }
  }
);

server.registerTool(
  "list_announcements",
  {
    title: "List Course Announcements",
    description: "Get announcements for courses. Announcements are discussion topics in the announcements context",
    inputSchema: {
      contextCodes: z.array(z.string()).describe("Context codes for courses (e.g., ['course_123', 'course_456'])"),
      startDate: z.string().optional().describe("Start date filter (ISO format)"), 
      endDate: z.string().optional().describe("End date filter (ISO format)")
    }
  },
  async ({ contextCodes, startDate, endDate }) => {
    try {
      const args: any = {
        query: { context_codes: contextCodes }
      };
      
      if (startDate) args.query.start_date = startDate;
      if (endDate) args.query.end_date = endDate;
      
      const { data } = await listAnnouncements.execute(args);
      return {
        content: [{ type: "text", text: JSON.stringify(data, null, 2) }]
      };
    } catch (error: any) {
      return {
        content: [{ type: "text", text: `Error: ${error.message}` }],
        isError: true
      };
    }
  }
);

server.registerTool(
  "list_course_users",
  {
    title: "List Course Users",
    description: "Get users enrolled in a specific course (students, teachers, TAs, etc.)",
    inputSchema: {
      courseId: z.string().describe("Canvas course ID"),
      enrollmentType: z.array(z.enum(["teacher", "student", "ta", "observer", "designer"])).optional().describe("Filter by enrollment type"),
      include: z.array(z.enum(["enrollments", "locked", "avatar_url", "test_student", "bio", "custom_links", "current_grading_period_scores", "uuid"])).optional().describe("Additional data to include")
    }
  },
  async ({ courseId, enrollmentType, include }) => {
    try {
      const args: any = {
        path: { course_id: courseId }
      };
      
      if (enrollmentType || include) {
        args.query = {};
        if (enrollmentType) args.query.enrollment_type = enrollmentType;
        if (include) args.query.include = include;
      }
      
      const { data } = await listUsersInCourseUsers.execute(args);
      return {
        content: [{ type: "text", text: JSON.stringify(data, null, 2) }]
      };
    } catch (error: any) {
      return {
        content: [{ type: "text", text: `Error: ${error.message}` }],
        isError: true
      };
    }
  }
);

// Main function to start the MCP server
async function main() {
  // Check for required environment variable
  if (!process.env.CANVAS_API_TOKEN) {
    console.error('Error: CANVAS_API_TOKEN environment variable required');
    console.error('Set it in your Claude Desktop config or run: export CANVAS_API_TOKEN="your_token_here"');
    process.exit(1);
  }

  const transport = new StdioServerTransport();
  await server.connect(transport);
  
  // Log to stderr so it doesn't interfere with MCP communication on stdout
  console.error("Canvas LMS MCP server running...");
}

main().catch((error) => {
  console.error("Error starting MCP server:", error);
  process.exit(1);
});