"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import {
  MessageSquare,
  Search,
  LayoutDashboard,
  ChevronDown,
  ChevronUp,
  Sparkles,
  PenSquare,
  Menu,
  X as CloseIcon,
} from "lucide-react";
import {
  Sheet,
  SheetContent,
  SheetTrigger,
  SheetTitle,
} from "@/components/ui/sheet";

interface SidebarProps {
  mode: "text" | "image" | "csv";
  setMode: (mode: "text" | "image" | "csv") => void;
  modes: Array<{ type: "text" | "image" | "csv"; label: string }>;
  isConnected?: boolean;
}

export default function Sidebar({
  mode,
  setMode,
  modes,
  isConnected = false,
}: SidebarProps) {
  const [isSingleChatOpen, setIsSingleChatOpen] = useState(true);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const chatHistory = [
    "build me a website f...",
    "build me a website...",
    "Please conduct an in...",
  ];

  const SidebarContent = () => (
    <aside className="w-56 flex flex-col gap-0 bg-sidebar text-sidebar-foreground h-full border-r border-border">
      {/* Logo Section */}
      <div className="p-4 flex items-center gap-2">
        <div className="w-8 h-8  flex items-center justify-center">
          <img src="/logo.jpeg" alt="II-Agent Logo" className="w-6 h-6" />
        </div>

        <div className="flex flex-col">
          <div className="flex items-center gap-2">
            <span className="font-semibold text-sm">II-Agent</span>
            <span className="text-[10px] bg-muted px-1.5 py-0.5 rounded">
              BETA
            </span>
          </div>
        </div>
      </div>

      {/* New Chat Button */}
      <div className="px-4 pb-3">
        <Button className="w-full bg-primary hover:bg-primary/90 text-primary-foreground justify-start gap-2">
          <PenSquare className="h-4 w-4" />
          New chat
        </Button>
      </div>

      {/* Navigation Items */}
      <div className="px-4 space-y-1">
        <Button
          variant="ghost"
          className="w-full justify-start gap-2 text-muted-foreground hover:text-foreground hover:bg-accent"
        >
          <Search className="h-4 w-4" />
          Search Chat
        </Button>
        <Button
          variant="ghost"
          className="w-full justify-start gap-2 text-muted-foreground hover:text-foreground hover:bg-accent"
        >
          <LayoutDashboard className="h-4 w-4" />
          Dashboard
        </Button>
      </div>

      {/* Single Chat Section */}
      <div className="px-4 mt-4">
        <Button
          variant="ghost"
          className="w-full justify-between text-muted-foreground hover:text-foreground hover:bg-accent border border-border rounded-md"
          onClick={() => setIsSingleChatOpen(!isSingleChatOpen)}
        >
          <div className="flex items-center gap-2">
            <MessageSquare className="h-4 w-4" />
            <span className="text-sm">Single Chat</span>
          </div>
          {isSingleChatOpen ? (
            <ChevronUp className="h-4 w-4" />
          ) : (
            <ChevronDown className="h-4 w-4" />
          )}
        </Button>

        {isSingleChatOpen && (
          <div className="mt-2 space-y-1 ml-2">
            {chatHistory.map((chat, idx) => (
              <Button
                key={idx}
                variant="ghost"
                className="w-full justify-start text-xs text-muted-foreground hover:text-foreground hover:bg-accent h-8 px-2 truncate"
              >
                {chat}
              </Button>
            ))}
          </div>
        )}
      </div>

      {/* Spacer */}
      <div className="flex-1" />

      {/* Plan Section */}
      <div className="p-4 border-t border-border">
        <div className="bg-muted/50 rounded-lg p-3 mb-2">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-xs bg-primary text-primary-foreground px-2 py-0.5 rounded">
              Free Plan
            </span>
          </div>
          <div className="flex items-center gap-2">
            <Sparkles className="h-4 w-4 text-muted-foreground" />
            <span className="text-xl font-bold">2,090</span>
          </div>
          <span className="text-xs text-muted-foreground">Credits</span>
        </div>
        <Button
          variant="outline"
          className="w-full"
        >
          <Sparkles className="h-4 w-4 mr-2" />
          Upgrade Plan
        </Button>
      </div>
    </aside>
  );

  return (
    <>
      {/* Mobile Menu Button - Only visible on mobile */}
      <div className="lg:hidden fixed top-4 left-4 z-40">
        <Sheet open={isMobileMenuOpen} onOpenChange={setIsMobileMenuOpen}>
          <SheetTrigger asChild>
            <Button
              variant="outline"
              size="icon"
              className="rounded-full bg-background"
            >
              <Menu className="h-5 w-5" />
            </Button>
          </SheetTrigger>
          <SheetContent side="left" className="p-0 w-56 bg-sidebar">
            <SheetTitle className="sr-only">Navigation Menu</SheetTitle>
            <SidebarContent />
          </SheetContent>
        </Sheet>
      </div>

      {/* Desktop Sidebar - Only visible on large screens */}
      <div className="hidden lg:block">
        <SidebarContent />
      </div>
    </>
  );
}
